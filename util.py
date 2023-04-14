import pdb
import sys

def readIntFromStr(str_input,min=1,max=-1):
    try:
        int_check = int(str_input)
        if int_check < min:
            if int_check > max and (max != -1):
                raise ValueError("\nInvalid number '{}' must be integer greater than {} and less than {}".format(nbins_input,min,max))
            else:
                raise ValueError("\nInvalid number '{}' must be integer greater than {}.".format(nbins_input,min))
        else:
            return int_check

    except Exception as e:
        #pdb.set_trace()
        print("\nInvalid number '{}' (must be an integer)".format(str_input)) 
        print("Returned error: {}".format(e))
        return -1

    return -1 # error

def listRequest(listitems,name):

    choice = ''
    while not choice:
            # show options
            request = "\n---------------------------------------------------\n"+\
                name+" Options\n---------------------------------------------------\n"
            enum_listitems = list(enumerate(listitems))
            list_formatted = ''.join(f'[{num+1}] {name}\n' for (num,name) in enum_listitems)
            #list_formatted = ''.join("\t [%s] %s \n" % ''.join(map(str,x)) for x,y in enumerate)
            print(request + list_formatted)
            print("\n---------------------------------------------------")
            # get user input
            user_selection = input("Type index of " +name.lower()+ ": ")
            if user_selection == 'q' or (user_selection == 'Q'):
                print("Quitting program.\n")
                sys.exit()
            index = readIntFromStr(user_selection,1,len(listitems)) # input only indices of available atype
            if index:
                choice = listitems[index-1]
    return choice