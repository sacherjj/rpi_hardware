## Raspberry Pi Hardware

This project is a collection of hardware drivers I have built for use with the Raspberry Pi hardware interface (both GPIO and SMB).

Unfortunately, GPIO is a Singleton interface to mimic the RPi.GPIO.  This makes testing difficult as every change modifies the state.  `GPIO.cleanup()` is implemented to reset all data and can be used to clean the object between runs or tests.

In addition, this includes some mock objects I've built to simulate GPIO and SMB interaction when you are not on an actual Pi.  This can be useful in working out hardware designs prior to laying out the PCB.   For example, `mocked.hcf4094` allow you to attach a callback function that will receive when pins change.  

On the testing side, I can give the HCF4094 device a mock GPIO object.  So all bit twidling is done virtually.  Now I can simulate that the hardware should do based on these values.  In my case this is applying charging power or pushing the power button on one of 144 tablets.  This will trigger a web service call with data.  So a full software simulation can be created that will allow me to test DB, workflow, and web side of a complex system without need of hardware.  It also allows me to unit test portions of workflow without hardware.

TDD with hardware is a lot of work and mocking, however if your down stream system is fairly complex, it still can be worth the effort.  
