## China Stock Money Flow Monitor

## PREREQUISITE
- git
- docker

## USAGE

### From Source
  - `git clone https://github.com/hadrianl/moneyFlowMonitor.git`
  - `cd moneyFlowMonitor`
  - `docker build -t money_flow_monitor .`
  - `docker run -t money_flow_monitor`
  
### From Docker Registry
  - `docker run -it --rm hadrianl/moneyflow`