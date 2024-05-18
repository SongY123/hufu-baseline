start() {
  if [[ "$OSTYPE" == "darwin"* ]]; then
    echo "block drop in proto tcp from any to any port $1" | sudo pfctl -ef -
    echo "block drop out proto tcp from any to any port $1" | sudo pfctl -ef -
  else
    sudo iptables -I INPUT -p tcp --dport $1
    sudo iptables -I OUTPUT -p tcp --sport $1
  fi
}

if [ ! -n "$1" ];then
  echo "Port cannot be empty!"
  echo "You can use the following command to monitor the port: sudo bash start.sh 8888"
  exit
fi

export PORT=$1
echo "Monitoring port: "  ${PORT}
start ${PORT}