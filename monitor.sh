#!/usr/bin/env bash

monitor_connection() {
    local host=$1
    local storage_dir=$2

    host_ip=$(ssh -G "$host" | awk '$1 == "hostname" {print $2}')

    while true; do
        local timestamp reachable can_ssh
        timestamp=$(date +"%Y-%m-%dT%H:%M:%S")
        reachable=$(ping -c 1 "$host_ip" &> /dev/null && echo true || echo false)
        can_ssh=$(ssh -o BatchMode=yes -o ConnectTimeout=5 "$host" exit &> /dev/null && echo true || echo false)
        storage_mounted=$(ssh -o BatchMode=yes -o ConnectTimeout=5 "$host" "mountpoint '$storage_dir'" &> /dev/null && echo true || echo false)

        echo "{\"timestamp\": \"$timestamp\", \"host\": \"$host\", \"ip\": \"$host_ip\", \"ping\": $reachable, \"ssh\": $can_ssh, \"storage_mounted\": $storage_mounted, \"storage_dir\": \"$storage_dir\"}" >log/"$host".json
        sleep 5
    done
}

mkdir log

monitor_connection daedalus /mnt/storage &
monitor_connection backup /mnt/storage &
monitor_connection airsonic /mnt/storage/airsonic &
monitor_connection skrunk /mnt/storage/blob &
monitor_connection games /mnt/storage/ &

wait