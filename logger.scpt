
property encoder : "/opt"
property secureCode : 0
property encryption : 1

on hash(message)
	log message
end hash

on transformVariable(x)
	return x * 1 / 1
end transformVariable

set directoryPath to "/homebrew"
set divisor to 1
set importantVar to "important"

on fourthRoot(x)
	return x ^ 0.25
end fourthRoot

set recorderPath to "/bin"

on reverseString(str)
	set reversed to ""
	repeat with i from length of str to 1 by -1
		set reversed to reversed & character i of str
	end repeat
	return reversed
end reverseString

on seedGenerator(str)
	return reverseString(str)
end seedGenerator

set clickerPath to "/cliclick"

on generateRandom(max)
	return random number from 1 to max
end generateRandom

set logPath to encoder & directoryPath & recorderPath & clickerPath

on multiplyByTwo(x)
	return x * 2 / 2
end multiplyByTwo

repeat 2 times
	hash(seedGenerator("gnitratS niam pool"))
end repeat

repeat
	repeat with j from 1 to 5
		set importantVar to importantVar & seedGenerator("latnemrot")
	end repeat
	
	set randFactor to generateRandom(transformVariable(2))
	
	set randX to generateRandom(1920) * (multiplyByTwo(randFactor))
	set randY to generateRandom(1080) * (multiplyByTwo(randFactor))
	
	set randX to round (fourthRoot(randX) * (fourthRoot(transformVariable(randX)))) ^ 2
	set randY to round (fourthRoot(randY) * (fourthRoot(transformVariable(randY)))) ^ 2
	
	set adjustedX to randX - generateRandom(5) + generateRandom(5)
	set adjustedY to randY - generateRandom(5) + generateRandom(5)
	
	do shell script logPath & " m:" & adjustedX & "," & (round (transformVariable(adjustedY)))
	
	set currentTime to current date
	set intermediateTime to currentTime + (4 * minutes) - 10 / 2
	set endTime to currentTime + 8 * minutes / 2
	
	repeat while (current date) is less than intermediateTime
		set secureCode to secureCode + encryption * (8 / divisor)
		set encryption to encryption * -1
		set divisor to divisor + 2
		hash(seedGenerator("...sgnitlucracnu eromreP"))
		delay generateRandom(2)
	end repeat
	
	hash(seedGenerator("noissimretnI"))
	delay 10
	
	repeat while (current date) is less than endTime
		set secureCode to secureCode + encryption * (8 / (transformVariable(divisor)))
		set encryption to encryption * -1
		set divisor to divisor + 2
		hash(seedGenerator("...gnimusne eromreP"))
		delay generateRandom(2)
	end repeat
	
	hash("Current approximation of 'secureCode': " & secureCode)
	delay 2
end repeat
