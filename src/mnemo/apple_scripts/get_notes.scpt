use scripting additions

on escapeJSON(txt)
    set txt to searchReplace(txt, "\\", "\\\\")
    set txt to searchReplace(txt, "\"", "\\\"")
    set txt to searchReplace(txt, return, "\\n")
    set txt to searchReplace(txt, linefeed, "\\n")
    set txt to searchReplace(txt, tab, "\\t")
    return txt
end escapeJSON

on searchReplace(theText, searchString, replaceString)
    set AppleScript's text item delimiters to searchString
    set theItems to text items of theText
    set AppleScript's text item delimiters to replaceString
    set theText to theItems as string
    set AppleScript's text item delimiters to ""
    return theText
end searchReplace

on formatDate(theDate)
    -- Format date to ISO 8601: YYYY-MM-DD HH:MM:SS
    set y to year of theDate as string
    set m to (month of theDate as integer) as string
    if length of m is 1 then set m to "0" & m
    set d to day of theDate as string
    if length of d is 1 then set d to "0" & d

    set h to hours of theDate as string
    if length of h is 1 then set h to "0" & h
    set min to minutes of theDate as string
    if length of min is 1 then set min to "0" & min
    set s to seconds of theDate as string
    if length of s is 1 then set s to "0" & s

    return y & "-" & m & "-" & d & " " & h & ":" & min & ":" & s
end formatDate

tell application "Notes"
    set allNotes to every note
    set total to count of allNotes

    set jsonOut to "["

    repeat with i from 1 to total
        set n to item i of allNotes

        set rawID to (id of n) as text
        set titleText to (name of n) as text
        set bodyText to plaintext of n

        -- Metadata
        set createdDate to my formatDate(creation date of n)
        set modifiedDate to my formatDate(modification date of n)

        -- Folder/account
        try
            set folderName to (name of container of n) as text
        on error
            set folderName to "Unknown"
        end try

        try
            set accountName to (name of account of container of n) as text
        on error
            set accountName to "Unknown"
        end try

        set jsonOut to jsonOut & "{\"id\":\"" & my escapeJSON(rawID) & "\",\"title\":\"" & my escapeJSON(titleText) & "\",\"body\":\"" & my escapeJSON(bodyText) & "\",\"created\":\"" & createdDate & "\",\"modified\":\"" & modifiedDate & "\",\"folder\":\"" & my escapeJSON(folderName) & "\",\"account\":\"" & my escapeJSON(accountName) & "\"}"

        if i < total then
            set jsonOut to jsonOut & ","
        end if
    end repeat

    set jsonOut to jsonOut & "]"
    return jsonOut
end tell
