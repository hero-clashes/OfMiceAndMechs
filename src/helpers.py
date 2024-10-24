import tcod

import src


def clamp(n, min, max):
    if n < min:
        return min
    if n > max:
        return max
    return n



def draw_frame_text(width, height, t, x, y):
    for cx in range(x-1,x+width):
        for cy in range(y-1,y+height):
            src.interaction.tcodConsole.rgb[cx,cy] = ord(" "), (0, 0, 0),(0, 0, 0) 
    for cx in range(x-1,x+width):
        src.interaction.tcodConsole.rgb[cx,y-1] = ord("-"), (255, 255, 255),(0, 0, 0) 
        src.interaction.tcodConsole.rgb[cx,y+height] = ord("-"), (255, 255, 255),(0, 0, 0) 
    for cy in range(y-1,y+height):
        src.interaction.tcodConsole.rgb[x-1,cy] = ord("|"), (255, 255, 255),(0, 0, 0) 
        src.interaction.tcodConsole.rgb[x+width,cy] = ord("|"), (255, 255, 255),(0, 0, 0) 

    src.interaction.tcodConsole.rgb[x-1,y-1] = ord("+"), (255, 255, 255),(0, 0, 0) 
    src.interaction.tcodConsole.rgb[x-1,y-2] = ord("|"), (255, 255, 255),(0, 0, 0) 
    src.interaction.tcodConsole.rgb[x-2,y-1] = ord("-"), (255, 255, 255),(0, 0, 0) 

    src.interaction.tcodConsole.rgb[x+width,y-1] = ord("+"), (255, 255, 255),(0, 0, 0) 
    src.interaction.tcodConsole.rgb[x+width,y-2] = ord("|"), (255, 255, 255),(0, 0, 0) 
    src.interaction.tcodConsole.rgb[x+width+1,y-1] = ord("-"), (255, 255, 255),(0, 0, 0) 
    
    src.interaction.tcodConsole.rgb[x-1,y+height] = ord("+"), (255, 255, 255),(0, 0, 0) 
    src.interaction.tcodConsole.rgb[x-1,y+height+1] = ord("|"), (255, 255, 255),(0, 0, 0) 
    src.interaction.tcodConsole.rgb[x-2,y+height] = ord("-"), (255, 255, 255),(0, 0, 0) 

    src.interaction.tcodConsole.rgb[x+width,y+height] = ord("+"), (255, 255, 255),(0, 0, 0) 
    src.interaction.tcodConsole.rgb[x+width,y+height+1] = ord("|"), (255, 255, 255),(0, 0, 0) 
    src.interaction.tcodConsole.rgb[x+width+1,y+height] = ord("-"), (255, 255, 255),(0, 0, 0) 


    src.interaction.tcodConsole.print_box(
        x,
        y,
        width,
        height,
        t,
        (255, 255, 255),
        (0, 0, 0),
        tcod.constants.BKGND_SET,
        tcod.constants.CENTER
    )
