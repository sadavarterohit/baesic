#It's the shell, it keeps taking input and runs it 
import baesic
while True :
    text = input('baesic > ')
    result, error = baesic.run('stdin',text)

    if error : print (error.as_string())
    elif result:
        print(result)

