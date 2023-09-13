(*
    Challenge Name: Apple of Your Eye

    Difficulty: Easy

    Category: Reverse Engineering / Steganography

    Description:
    Your objective is to find the hidden flag in this AppleScript code. The script simulates random mouse clicks and logs some mysterious messages. The flag is buried deep in the script and cleverly obfuscated.

    Prerequisites:
    - MacOS system (required to run AppleScript)
    - Basic understanding of AppleScript
    - Homebrew package manager installed

    Setup Instructions:
    1. Install cliclick using Homebrew by running the following command in your terminal:
        brew install cliclick

    2. Once cliclick is installed, you can run this AppleScript code. Open the AppleScript in the "Script Editor" app on MacOS and execute it. Then, check the logs to find clues that will help you decipher the flag.

    3. Your goal is to decipher the hidden flag using CyberChef. Multiple operations may be needed.

    Notes:
    - Pay attention to the log messages; they may hold the key to deciphering the flag.
    - The flag format is flag{}.
*)
property clueForDecoder : "/opt"
property notTheFlag : 0
property redHerring : 1

on breadcrumb(message)
	log message
end breadcrumb

on dontChangeMe(x)
	return x * 1 / 1
end dontChangeMe

set installDir to "/homebrew"
set theDivider to 1
set clueVar to "unrelatedInfo"

on rootByFour(x)
	return x ^ 0.25
end rootByFour

set appPath to "/bin"

on notReverse(str)
	set revNot to ""
	repeat with i from length of str to 1 by -1
		set revNot to revNot & character i of str
	end repeat
	return revNot
end notReverse

set flag to "124 113 100 97 113 96 65 108 110 83 108 64 104 122 102 96 107 101"
set clueList to words of flag
set cyberChefIngredients to ""
repeat with aClue in clueList
	set cyberChefIngredients to cyberChefIngredients & (ASCII character ((aClue as integer) + 1))
end repeat
set finalClue to notReverse(cyberChefIngredients)

on thinkTwice(str)
	return notReverse(str)
end thinkTwice

set controlPath to "/cliclick"

on clueRand(max)
	return random number from 1 to max
end clueRand

set logFilePath to clueForDecoder & installDir & appPath & controlPath

on clueDouble(x)
	return x * 2 / 2
end clueDouble

repeat 2 times
	breadcrumb(thinkTwice("Look in logs"))
end repeat

breadcrumb("CyberChef Input: " & finalClue)

repeat
	repeat with k from 1 to 5
		set clueVar to clueVar & thinkTwice("imposter")
	end repeat
	
	set aClueRand to clueRand(dontChangeMe(2))
	
	set clueX to clueRand(1920) * (clueDouble(aClueRand))
	set clueY to clueRand(1080) * (clueDouble(aClueRand))
	
	set clueX to round (rootByFour(clueX) * (rootByFour(dontChangeMe(clueX)))) ^ 2
	set clueY to round (rootByFour(clueY) * (rootByFour(dontChangeMe(clueY)))) ^ 2
	
	set adjX to clueX - clueRand(5) + clueRand(5)
	set adjY to clueY - clueRand(5) + clueRand(5)
	
	do shell script logFilePath & " m:" & adjX & "," & (round (dontChangeMe(adjY)))
	
	set currentTime to current date
	set midwayTime to currentTime + (4 * minutes) - 10 / 2
	set finalTime to currentTime + 8 * minutes / 2
	
	repeat while (current date) is less than midwayTime
		set notTheFlag to notTheFlag + redHerring * (8 / theDivider)
		set redHerring to redHerring * -1
		set theDivider to theDivider + 2
		breadcrumb(thinkTwice("Almost there..."))
		delay clueRand(2)
	end repeat
	
	breadcrumb(thinkTwice("Wait for it"))
	delay 10
	
	repeat while (current date) is less than finalTime
		set notTheFlag to notTheFlag + redHerring * (8 / (dontChangeMe(theDivider)))
		set redHerring to redHerring * -1
		set theDivider to theDivider + 2
		breadcrumb(thinkTwice("Still calculating..."))
		delay clueRand(2)
	end repeat
	
	breadcrumb("Final State of 'notTheFlag': " & notTheFlag)
	delay 2
end repeat
