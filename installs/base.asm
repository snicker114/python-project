IDEAL

MODEL small
STACK 256


DATASEG

CODESEG
    ORG 100h
start:
	 mov ax, @data
	 mov ds,ax
	 
    ; here your code
	 
	
EXIT:
    
	mov ax, 4C00h ; returns control to dos
  	int 21h
  
  
;---------------------------
; Procudures area
;---------------------------
 

END start