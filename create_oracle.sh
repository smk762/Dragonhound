#!/bin/bash
# A Simple TUI for creating an oracle on a selected chain.

col_red="\e[31m"
col_green="\e[32m"
col_yellow="\e[33m"
col_blue="\e[34m"
col_magenta="\e[35m"
col_cyan="\e[36m"
col_default="\e[39m"
col_ltred="\e[91m"
col_dkgrey="\e[90m"
colors=($col_red $col_green $col_yellow $col_blue $col_magenta $col_cyan)

initTime=$SECONDS

if [[ ! -d $HOME/.komodo/oracle_logs ]]; then
  mkdir $HOME/.komodo/oracle_logs
fi

ac_json=$(cat "$HOME/StakedNotary/assetchains.json")
for chain_params in $(echo "${ac_json}" | jq  -c -r '.[]'); do
  ac_name=$(echo $chain_params | jq -r '.ac_name')
  ac_list+=($ac_name)
done

echo -e -n "$col_blue"
PS3="Chain to create oracle on: "
select ac in "${ac_list[@]}"
do
    echo -e -n "$col_yellow"
    ac_name=$ac
    cli="komodo-cli -ac_name=$ac_name"
    ac_balance=$($cli getbalance)
    break
done
echo "$ac_name selected ($ac_balance)"

name=""
while [[ $name == "" ]]; do
  echo -e -n "${col_blue}Oracle name: ${col_default}"
  read name
done
echo "NAME: $name"

desc=""
while [[ $desc == "" ]]; do
  echo -e -n "${col_blue}Oracle description: ${col_default}"
  read desc
done
echo "DESC: $desc"

formats=("s = < 256 char string" "S = <65536 char string" "d = <256 binary data" "D = <65536 binary data" "c = 1 byte signed little endian number" "t = 2 byte signed little endian number" "i = 4 byte signed little endian number" "l = 8 byte signed little endian number" "C = 1 byte unsigned little endian number" "T = 2 byte unsigned little endian number" "I = 4 byte unsigned little endian number" "L = 8 byte unsigned little endian number" "h = 32 byte hash")
echo -e -n "$col_blue"
PS3="Oracle format: "
select format_desc in "${formats[@]}"
do
	format=${format_desc:0:1}
	if [[ $format != "" ]]; then
		break
	fi
done
#echo "format_desc: $format_desc"
#echo "format: $format"

oracle=$($cli oraclescreate "$name" "$desc" "$format")
#echo $oracle
oracleHex=$(echo $oracle | jq -r '.hex')
#echo $oracleHex
oracleResult=$(echo $oracle | jq -r '.result')
#echo $oracleResult
while [[ $oracleResult != "success" ]]; do
	sleep 7
	oracle=$(echo $cli oraclescreate "${name}" "${desc}" "${format}")
	#echo $oracle
	oracleHex=$(echo $oracle | jq -r '.hex')
	#echo $oracleHex
	oracleResult=$(echo $oracle | jq -r '.result')
	#echo $oracleResult
	echo "creating oracle..."
done
oracleTX=$($cli sendrawtransaction $oracleHex)
memPool=$($cli getrawmempool)
match=$(echo $memPool | grep "$oracleTX")
while [[ $match == "" ]]; do
	sleep 7
	memPool=$($cli getrawmempool)
	match=$(echo $memPool | grep $oracleTX)
	echo "Confirming in mempool..."
done 
echo "Oracle creation tx confirmed"
oraclesList=$($cli oracleslist)
match=$(echo $oraclesList | grep $oracleTX)
while [[ $match == "" ]]; do
	sleep 7
	oraclesList=$($cli oracleslist)
	#echo "oraclesList: $oraclesList"
	match=$(echo $oraclesList | grep $oracleTX)
	#echo "oracleTX: $oracleTX"
	echo "Listing on $ac_name in mempool..."
done 
echo "Oracle listed on $ac_name"
oraclesInfo=$($cli oraclesinfo $oracleTX)

datafee=1000000 # in satoshis
echo "Registering Oracle subscription plan"
oracleReg=$($cli oraclesregister $oracleTX $datafee)
#echo "oracleReg: $oracleReg"
regHex=$(echo $oracleReg | jq -r '.hex')
#echo "regHex: $regHex"
regResult=$(echo $oracleReg | jq -r '.result')
#echo "regResult: $regResult"
while [[ $regResult != "success" ]]; do
	sleep 7
	oracleReg=$($cli oraclesregister $oracleTX $datafee)
	#echo "oracleReg: $oracleReg"
	regHex=$(echo $oracleReg | jq -r '.hex')
	#echo "regHex: $regHex"
	regResult=$(echo $oracleReg | jq -r '.result')
	#echo "regResult: $regResult"
	echo "awaiting registration..."
done

oracleRegTX=$($cli sendrawtransaction $regHex)
memPool=$($cli getrawmempool)
match=$(echo $memPool | grep "$oracleRegTX")
while [[ $match == "" ]]; do
	sleep 7
	memPool=$($cli getrawmempool)
	match=$(echo $memPool | grep $oracleRegTX)
	#echo "oracleRegTX: $oracleRegTX"
	echo "checking mempool for confirmation"
done 
echo "Oracle registration tx in mempool"

oraclesInfo=$($cli oraclesinfo $oracleTX)
publisher=$(echo $oraclesInfo | jq  '.registered' | jq -r '.[].publisher')
while [[ $publisher == "" ]]; do
	sleep 7
	oraclesInfo=$($cli oraclesinfo $oracleTX)
	publisher=$(echo $oraclesInfo | jq  '.registered' | jq -r '.[].publisher')
	echo "Getting publisher ID..."
done

echo "Subscribing to oracle"
datafee=100 # not in satoshis?
oracleSub=$($cli oraclessubscribe $oracleTX $publisher $datafee)
#echo "oracleSub: $oracleSub"
subHex=$(echo $oracleSub | jq -r '.hex')
#echo "subHex: $subHex"
subResult=$(echo $oracleSub | jq -r '.result')
#echo "subResult: $subResult"
while [[ $subResult != "success" ]]; do
	sleep 7
	#echo "$oracleTX / $publisher / $datafee"
	oracleSub=$($cli oraclessubscribe $oracleRegTX $publisher $datafee)
	#oracleSub=$($cli oraclessubscribe $oracleTX $publisher $datafee)
	#echo "oracleSub: $oracleSub"
	subHex=$(echo $oracleSub | jq -r '.hex')
	#echo "subHex: $subHex"
	subResult=$(echo $oracleSub | jq -r '.result')
	#cho "subResult: $subResult"	
	echo "verifying registration completed..."
done

echo "Confirming subscription"

oracleSubTX=$($cli sendrawtransaction $subHex)
memPool=$($cli getrawmempool)
match=$(echo $memPool | grep "$oracleSubTX")
while [[ $match == "" ]]; do
	sleep 7
	memPool=$($cli getrawmempool)
	match=$(echo $memPool | grep $oracleSubTX)
	echo "checking mempool for confirmation..."
done 


echo "Oracle subscription tx confirmed"

echo "==========="
echo "ORACLE INFO"
echo "==========="
echo $oraclesInfo | jq '.'
echo "==========="
