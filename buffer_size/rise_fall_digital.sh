sed "s/nf_load/$1/g" $4.template > $4.temp
sed "s/cap_load/$2/g" $4.temp > $4.temp2
sed "s/vdd_val/$3/g" $4.temp2 > $4.ocn
ocean -replay $4.ocn -nograph - log ./log/log.txt
