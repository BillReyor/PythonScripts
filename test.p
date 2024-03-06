DEFINE VARIABLE n AS INTEGER NO-UNDO.
DEFINE VARIABLE i AS INTEGER NO-UNDO.
DEFINE VARIABLE result AS INTEGER NO-UNDO.

DISPLAY "Enter a number: " WITH FRAME user-input.
UPDATE n WITH FRAME user-input.

ASSIGN result = 1.

DO i = 1 TO n:
    ASSIGN result = result * i.
END.

DISPLAY "The factorial of " n " is " result.
