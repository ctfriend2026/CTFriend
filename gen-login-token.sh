#!/bin/bash

in_file="email-list.txt"
out_file="email-token-list.txt"

rm email-token-list.txt 2> /dev/null

# read emails from email-list.txt
while IFS= read -r email || [[ -n "$email" ]]; do
    # skip empty lines
    [[ -z "$email" ]] && continue  

    email=$(echo "$email" | xargs)

    # add each email to the whitelist (within ctfriend)
    # parse the token from the output
    token=$(docker exec ctfriend python3 app/token_manager.py whitelist \
        $email | awk -F': ' '/token is:/ {print $2}' )

    echo $email " " $token

    # save to file email-token-list.txt
    printf "%-25s %-64s\n" "$email" "$token" >> "$out_file"
done < "$in_file" 

