## Raspberry Pi Hardware

This project is a collection of hardware drivers I have built for use with the Raspberry Pi hardware interface (both GPIO and SMB).

In addition, this includes some mock objects I've built to simulate GPIO and SMB interaction when you are not on an actual Pi.  This can be useful in working out hardware designs prior to laying out the PCB.

An example of this is a complex design I created with the HCF4094 shift register.  If you chain these chips together, the interface is exactly the same, you just shift more bits.  I have 36 HCF4094 devices connected together on 6 boards of 6 devices each.  All I need to do is call the shift_data with a tuple/list of 288 bit values.

I use an ordered dictionary, with entries in the correct order, so it is easy to set the values but name and then shift them out in the correct order. 

On the testing side, I can give the HCF4094 device a mock GPIO object.  So all bit twidling is done virtually.  Now I can simulate that the hardware should do based on these values.  In my case this is applying charging power or pushing the power button on one of 144 tablets.  This will trigger a web service call with data.  So a full software simulation can be created that will allow me to test DB, workflow, and web side of a complex system without need of hardware.  It also allows me to unit test portions of workflow without hardware.

TDD with hardware is a lot of work and mocking, however if your down stream system is fairly complex, it still can be worth the effort. 
