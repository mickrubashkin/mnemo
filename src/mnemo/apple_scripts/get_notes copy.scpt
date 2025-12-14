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

tell application "Notes"
    set allNotes to every note
    set total to count of allNotes

    set jsonOut to "["

    repeat with i from 1 to total
        set n to item i of allNotes

        set rawID to (id of n) as text
        set titleText to (name of n) as text
        set bodyText to plaintext of n

        set jsonOut to jsonOut & "{\"id\":\"" & my escapeJSON(rawID) & "\",\"title\":\"" & my escapeJSON(titleText) & "\",\"body\":\"" & my escapeJSON(bodyText) & "\"}"

        if i < total then
            set jsonOut to jsonOut & ","
        end if
    end repeat

    set jsonOut to jsonOut & "]"
    return jsonOut
end tell
