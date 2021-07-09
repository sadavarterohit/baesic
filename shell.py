#It's the shell, it keeps taking input and runs it 
import baesic
while True :
    text = input('baesic > ')
    if text.strip=="":
        continue
    result, error = baesic.run('stdin',text)

    if error : print (error.as_string())
    elif result:
        if len(result.elements) ==1:
            print(repr(result.elements[0]))
        else:
            print(repr(result))

