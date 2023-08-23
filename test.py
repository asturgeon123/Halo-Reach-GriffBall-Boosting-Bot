from rgbprint import gradient_print, Color, rgbprint




logo_text = """ __  __     ______     __         ______        ______     ______     ______  
/\ \_\ \   /\  __ \   /\ \       /\  __ \      /\  == \   /\  __ \   /\__  _\ 
\ \  __ \  \ \  __ \  \ \ \____  \ \ \/\ \     \ \  __<   \ \ \/\ \  \/_/\ \/ 
 \ \_\ \_\  \ \_\ \_\  \ \_____\  \ \_____\     \ \_____\  \ \_____\    \ \_\ 
  \/_/\/_/   \/_/\/_/   \/_____/   \/_____/      \/_____/   \/_____/     \/_/ 
  """

author = """        An autonomous farming bot that plays griffball in Halo Reach
                        ______________________________
                        |                            |
                        | Created by: @Alex Sturgeon | 
                        |____________________________|

-----------------------------------------------------------------------------
"""

gradient_print(logo_text+author, 
    start_color=0x4BBEE3, 
    end_color=Color.medium_violet_red
)


#rgbprint(author, color=Color.medium_violet_red)