import requests
import pandas as pd
import numpy as np
import datetime as dt
import time
from rich.console import Console
from rich.table import Table
from rich.live_render import LiveRender

his_flow_url = 'http://push2his.eastmoney.com/api/qt/kamt.kline/get?fields1=f1,f3,f5&fields2=f51,f52&klt=101&lmt=300'

realtime_flow_url = 'http://push2.eastmoney.com/api/qt/kamt.rtmin/get?fields1=f1,f3&fields2=f51,f52,f54,f56'

def get_history_money_flow(url):
    ret = requests.get(his_flow_url)

    if not ret.ok:
        raise '请求历史资金流向失败！'
        
    result_df = {}

    for name, values in ret.json()['data'].items():
        result_df[name] = pd.DataFrame.from_records(map(lambda v: v.split(','), values), columns=['datetime', 'value']).set_index('datetime').astype(float)

    return result_df

def calc_his_statistics(money_flow, windows=250):
    statistics = {}

    for name, df in money_flow.items():
        rolled = df.rolling(250)
        statistics[name] = [rolled.mean().iloc[-1]['value'], rolled.std().iloc[-1]['value']]

    return statistics

def get_realtime_money_flow(realtime_flow_url):
    ret = requests.get(realtime_flow_url)

    if not ret.ok:
        raise '请求实时资金流向失败！'

    data = ret.json()['data']

    _date = dt.datetime(dt.datetime.today().year, *map(int, data['s2nDate'].split('-')))

    result_df = pd.DataFrame(map(lambda v: v.split(','), data['s2n']), columns=['time', 'hk2sh', 'hk2sz', 's2n']).\
        set_index('time').replace('-', np.nan).dropna().astype(float)

    return result_df

if __name__ == "__main__":
    console = Console()
    lr = LiveRender(None)
    stat_table = Table(title='历史北向资金净流入统计', show_header=True, header_style="bold blue")
    stat_table.add_column("Name")
    stat_table.add_column("Mean")
    stat_table.add_column("Std")
    console.print(f"历史北向资金流向url：{his_flow_url}")
    console.print(f"实时北向资金流向url：{realtime_flow_url}")


    his_money_flow = get_history_money_flow(his_flow_url)
    statistics = calc_his_statistics(his_money_flow)
    for name, stats in statistics.items():
        stat_table.add_row(name, *map(str, stats))

    console.print(stat_table)

    while True:
        try:
            df = get_realtime_money_flow(realtime_flow_url)
        except:
            time.sleep(60)
            continue

        pc = lr.position_cursor()  # mark down the beggin
        realtime_flow_table = Table(title='实时北向资金净流入', show_header=True, header_style="bold blue")

        realtime_flow_table.add_column('Time')
        for c in df.columns:
            realtime_flow_table.add_column(c)

        latest_data = df.iloc[-5:]
        for t, flows in latest_data.iterrows():
            realtime_flow_table.add_row(t, *flows.astype(str))


        if not latest_data.empty:
            last = latest_data.iloc[-1]

            mul_stds = []
            for n, v in last.items():
                mul_std = (v - statistics[n][0]) / statistics[n][1]
                mul_stds.append(f'[bold red]{mul_std:.3f}[/bold red]' if abs(mul_std) > 1.5 else f'[bold magenta]{mul_std:.3f}[/bold magenta]')

            realtime_flow_table.add_row('STD', *mul_stds)
            
        lr.set_renderable(realtime_flow_table)
        console.print(pc)
        console.print(lr)
            


        time.sleep(60)
