#It's the shell, it keeps taking input and runs it 
import baesic
while True :
    text = input('baesic > ')
    result, error = baesic.run(text)

    if error : print (error.as_string())
    else:
        print(result)