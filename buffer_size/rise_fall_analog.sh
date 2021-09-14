sed "s/cap_load/$1/g" $3.template > $3.temp
sed "s/vdd_val/$2/g" $3.temp > $3.ocn
ocean -replay $3.ocn -nograph - log ./log/log.txt
