use scripting additions

on escapeJSON(t)
    -- escape backslashes and quotes
    set t to my replaceText(t, "\\", "\\\\")
    set t to my replaceText(t, "\"", "\\\"")

    -- remove Notes attachments (OBJECT REPLACEMENT CHARACTER)
    set t to my replaceText(t, "￼", "") -- U+FFFC
    set t to my replaceText(t, "�", "") -- U+FFFD

    -- nbsp
    set nbsp to (ASCII character 160)
    set t to my replaceText(t, nbsp, " ")

    -- zero-width chars
    set t to my replaceText(t, "​", "")
    set t to my replaceText(t, "‌", "")
    set t to my replaceText(t, "‍", "")
    set t to my replaceText(t, "﻿", "")

    -- JSON special separators
    set t to my replaceText(t, " ", "\\n") -- U+2028
    set t to my replaceText(t, " ", "\\n") -- U+2029

    -- tabs
    set t to my replaceText(t, (ASCII character 9), "\\t")

    -- control characters < 0x20 except \n, \r, \t
    repeat with i from 0 to 31
        if i is not 9 and i is not 10 and i is not 13 then
            set t to my replaceText(t, (ASCII character i), "")
        end if
    end repeat

    -- tabs and eof
    set t to my replaceText(t, return, "\\n")
    set t to my replaceText(t, linefeed, "\\n")

    return t
end escapeJSON

on replaceText(theText, search, rep)
    set AppleScript's text item delimiters to search
    set parts to text items of theText
    set AppleScript's text item delimiters to rep
    set newText to parts as string
    set AppleScript's text item delimiters to ""
    return newText
end replaceText

tell application "Notes"
    set allNotes to every note
    set total to count of allNotes
    set out to "["

    repeat with i from 1 to total
        set n to item i of allNotes

        set noteTitle to my escapeJSON(name of n)
        set noteBody to my escapeJSON(plaintext of n)
        set noteID to my escapeJSON(id of n)

        set out to out & "{\"id\":\"" & noteID & "\",\"title\":\"" & noteTitle & "\",\"body\":\"" & noteBody & "\"}"

        if i < total then
            set out to out & ","
        end if
    end repeat

    set out to out & "]"
    return out
end tell
