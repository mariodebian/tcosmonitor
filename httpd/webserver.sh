#!/bin/sh

port=8081
network_interface=eth0


if [ ! -f system-info.tpl ]; then
  # working on real busybox
  . /scripts/functions
  . /conf/tcos.conf
  . /conf/tcos-run-functions
  www=/var/www/
  conffile=/etc/httpd.conf
  system_info=${www}/system-info.xml
  system_template=/etc/system-info.tpl
  IFCONFIG="busybox ifconfig"
else
  # working n svn dir
  echo "DEBUG: working on SVN dir"
  . /usr/share/initramfs-tools/scripts/functions
  . /etc/tcos/tcos.conf
  . /etc/tcos/tcos-run-functions
  www=./
  conffile=./httpd.conf
  system_info=${www}/system-info.xml
  system_template=./system-info.tpl
  IFCONFIG="/sbin/ifconfig"
fi

start_server() {
  mkdir -p /var/log
  busybox httpd -p ${port} -c ${conffile} -h ${www} >> /var/log/webserver.log 2>&1
}

stop_server() {
  killall httpd
}

read_lspci() {
  echo $(lspci | head -$1|tail -1)
}

write_into_xml() {
 # $1 is key
 # $2 is value
 # $3 is block to add before (optional)
 # $4 is block name <$4></$4>
 if [ ! -f ${system_info} ]; then
   cp ${system_template} ${system_info}
 fi
 if [ -z "$3" ]; then
   key=__${1}__
   value="${2}"
   sed -i "s/${key}/${value}/g" ${system_info}
 else
   cat ${system_info} | sed "/<${3}>/a\
<${4}>${2}</${4}>
" > ${system_info}_1
   mv ${system_info}_1 ${system_info}
 fi
}



get_system_info() {

 cpu_model=$(grep "^model name" /proc/cpuinfo | awk -F ": " '{print $2}')
 write_into_xml "cpu_model" "${cpu_model}"

 cpu_speed=$(grep "^cpu MHz" /proc/cpuinfo | awk -F ": " '{print $2" MHz"}')
 write_into_xml "cpu_speed" "${cpu_speed}"

 cpu_vendor=$(grep "^vendor_id" /proc/cpuinfo | awk -F ": " '{print $2}')
 write_into_xml "cpu_vendor" "${cpu_vendor}"


 ram_total=$(grep ^MemTotal /proc/meminfo | awk '{print $2" "$3}')
 write_into_xml "ram_total" "${ram_total}"

 ram_active=$(grep ^Active /proc/meminfo | awk '{print $2" "$3}')
 write_into_xml "ram_active" "${ram_active}"

 ram_free=$(busybox free| grep "Mem:"| awk '{print $4" kB"}')
 write_into_xml "ram_free" "${ram_free}"

 ram_used=$(busybox free| grep "Mem:"| awk '{print $3" kB"}')
 write_into_xml "ram_used" "${ram_used}"

 swap_avalaible=$(grep -c ^/ /proc/swaps)
 if [ $swap_avalaible -gt 0 ]; then
   write_into_xml "swap_avalaible" "1"
 else
   write_into_xml "swap_avalaible" "0"
 fi

 swap_total=$(free| grep "Swap:"| awk '{print $2" kB"}')
 write_into_xml "swap_total" "${swap_total}"

 swap_used=$(free| grep "Swap:"| awk '{print $3" kB"}')
 write_into_xml "swap_used" "${swap_used}"

 swap_free=$(free| grep "Swap:"| awk '{print $4" kB"}')
 write_into_xml "swap_free" "${swap_free}"

 tcos_date=$(LANG=C date)
 write_into_xml "tcos_date" "${tcos_date}"

 write_into_xml "tcos_generation_date" "${TCOS_DATE}"
 write_into_xml "tcos_version" "${TCOS_VERSION}"

 network_hostname=$(hostname)
 write_into_xml "network_hostname" "${network_hostname}"

 network_ip=$(${IFCONFIG} ${network_interface}| grep "inet addr:"| awk '{print $2}'| awk -F ":" '{print $2}')
 write_into_xml "network_ip" "${network_ip}"

 network_mac=$(${IFCONFIG} ${network_interface}| grep "HWaddr"| awk '{print $5}')
 write_into_xml "network_mac" "${network_mac}"

 network_mask=$(${IFCONFIG} ${network_interface}| grep "inet addr:"| awk '{print $4}'| awk -F ":" '{print $2}')
 write_into_xml "network_mask" "${network_mask}"

 network_rx=$(${IFCONFIG} ${network_interface}|grep "RX bytes"| awk '{print $3" "$4}'| sed s/"("//g| sed s/")"//g)
 write_into_xml "network_rx" "${network_rx}"

 network_tx=$(${IFCONFIG} ${network_interface}|grep "TX bytes"| awk '{print $7" "$8}'| sed s/"("//g| sed s/")"//g)
 write_into_xml "network_tx" "${network_tx}"

 #FIXME read from /proc/partitions instead of use fdisk
 #devices=$(grep ^/dev /etc/fstab| awk '{print $1":"$3}')
 #for device in ${devices}; do
 # dev=$(echo $device| awk -F ":" '{print $1}')
 # type=$(echo $device| awk -F ":" '{print $2}')
 # size1=$(/sbin/fdisk -l |grep ${dev} | awk '{print $4}' | sed s/"+"/""/g)
 # if [ -z "${size1}" ]; then
 #   size1=0
 # fi
 # size=$(($size1 / 1000 ))
 # write_into_xml "$dev" "$type:$size" "disk_tree" "part"
 #done


 #FIXME need a way to know split files with "XX.XX.XX text text text"
 _max=$(lspci | wc -l)
 number=8
 counter=1
 bus_ids=""
 for line in $(seq 1 $_max); do
   bus=$(read_lspci $line)
   bus_id=$(expr substr "${bus}" 1 $((${number}-1)))
   if [ $counter -gt 2 ]; then
     bus_ids="${bus_ids} ${bus_id}"
   else
     bus_ids="${bus_id}"
   fi
   txt=$(expr substr "${bus}" $((${number}+1)) 100)
   write_into_xml "$bus_id" "$txt" "pci_bus" "pci_busid_$(echo ${bus_id} | sed s/":"/"_"/g)"
   counter=$((counter +1))
 done
 write_into_xml "pci_bus_ids" "${bus_ids}"

 
 #modules_info=""
 #modules=$(cat /proc/modules| awk '{print $1}')
 #for line in ${modules}; do
 # modules_info="${modules} ${line}"
 #done

 #write_into_xml "modules_info" "${modules_info}" 
}

get_process() {
 # $1 is process name
 is_running=$(ps aux |grep "$1"| grep -v grep | wc -l)
 if [ ${is_running} -gt 0 ]; then
   write_into_xml "$1" "1" "process_tree" "process"
 fi
}



if [ "$1" = "" ]; then
 echo "$(date) Starting webserver.sh" >> /var/log/webserver.log
 mkdir -p ${www}
 rm -f ${system_info}
 start_server
 get_system_info
fi

if [ "$1" = "update" ]; then
 echo "$(date) Updating server-info" >> /var/log/webserver.log
 rm -f ${system_info}
 get_system_info
fi

if [ "$1" = "stop" ]; then
 echo "$(date) Stopping webserver.sh" >> /var/log/webserver.log
 stop_server
fi


exit 0
