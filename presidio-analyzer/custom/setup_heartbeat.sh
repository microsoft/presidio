
export HB_PORT=21230
echo Heartbeat port: $HB_PORT

function hasHeartbeat {
  c=$(netstat -an | grep ${HB_PORT} | grep -i ESTABLISHED)
  if [[ -n $c ]]; then
    echo yes
  else
    echo no
  fi

}

function hasListener {
  c=$(netstat -an | grep ${HB_PORT} | grep -i LISTEN)
  if [[ -n $c ]]; then
    echo yes
  else
    echo no
  fi
}

function heartbeat_loop {
  pkill nc
  sleep 1
  while :; do sleep 1; done | nc -l ${HB_PORT} > /dev/null 2>&1 &

  # 5 Second wait before proceeding
  echo 5 second sleep...
  sleep 5


  # 30 minute wait before terminating Presidio container
  time_remaining=1800
  while (( time_remaining-- > 0 ))
  do
    echo Wait for Heartbeat. Time remaining: "$time_remaining"
    [[ $(hasHeartbeat) == yes  ]] && {
      break;
    }
    [[ $(hasListener) == no && $(hasHeartbeat) == no  ]] && {
      echo Heartbeat unavailable. hasListener: "$hasListener" hasHeartbeat: "$hasHeartbeat"
      return 1
    }
    sleep 1
  done

  if (( time_remaining <= 0 ))
  then
    echo Heartbeat connection timeout.
    return 1
  fi

  echo Heartbeat connected.

  heartbeat_count=0

  while (( ++heartbeat_count > 0 ))
  do
    echo Heartbeat count: "$heartbeat_count"
    [[ $(hasHeartbeat) == no  ]] && {
      break;
    }
    sleep 1
  done

  echo Heartbeat stopped. Terminating ...

  return 0
}

heartbeat_loop
RET=$?
echo RET=$RET
exit $RET
