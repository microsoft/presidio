
export HB_PORT=21230
function hasHeartbeat {
  c=$(netstat -an | grep ${HB_PORT} | grep -i ESTABLISHED)
  if [[ -n $c ]]; then
    echo yes
  else
    echo no
  fi

}

function heartbeat_loop {
  pkill nc
  sleep 1
  #nc -k -l -p ${HB_PORT} > /dev/null 2>&1 &            //different linux version?
  #nc -k -l ${HB_PORT} > /dev/null 2>&1 &             // dont send to standard output
  nc -k -l -d ${HB_PORT} &

  #30 minute wait time
  #let l=1800
  let l=20

  while (( l-- > 0 ))
  do
    echo wait for heartbeat $l
    [[ $(hasHeartbeat) == yes  ]] && {
      break;
    }
    sleep 1
  done

  if (( l <= 0 ))
  then
    echo heartbeat connection timeout.
    return 1
  fi

  echo heartbeat connected.

  l=0

  while (( ++l > 0 ))
  do
    echo heart is beating $l
    [[ $(hasHeartbeat) == no  ]] && {
      break;
    }
    sleep 1
  done

  echo Heartbeat stopped. Terminating ...
  return 0
}

heartbeat_result=1
while((heartbeat_result!=0));
do
  heartbeat_result=heartbeat_loop
  sleep 1
done
