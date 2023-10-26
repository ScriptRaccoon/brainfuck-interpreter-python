          # brainfuck program for adding 2 and 3 
++.       # write 2 to the first cell and print it (as ascii char)
>         # go to the next cell 
+++.      # write 3 to the second cell and print it (as ascii char)
[<+>-]    # loop: put the content of second cell on the first cell
<.        # go back to the first cell and print the content (as ascii char)