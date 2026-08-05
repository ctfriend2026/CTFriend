#!/bin/bash
# Bulk token-generation helper for CTFriend.
# Reads email-list.txt, whitelists each email, and writes tokens to email-token-list.txt.

in_file="email-list.txt"
out_file="email-token-list.txt"

# Start with a fresh output file for this run.
rm email-token-list.txt 2> /dev/null

# Read emails from email-list.txt.
while IFS= read -r email || [[ -n "$email" ]]; do
    # Skip empty lines.
    [[ -z "$email" ]] && continue  

    # Trim surrounding whitespace before passing the email into the container.
    email=$(echo "$email" | xargs)

    # Add each email to the whitelist inside ctfriend and parse the token.
    token=$(docker exec ctfriend python3 app/token_manager.py whitelist \
        $email | awk -F': ' '/token is:/ {print $2}' )

    echo $email " " $token

    # Save the email/token pair to email-token-list.txt.
    printf "%-25s %-64s\n" "$email" "$token" >> "$out_file"
done < "$in_file" 
