import spidev
import time
spi = spidev.SpiDev()
spi.open(0,0)

# read SPI data from MCP3008 chip, 8 possible adc's (0 thru 7)
def readadc(adcnum):
        if ((adcnum > 7) or (adcnum < 0)):
                return -1
        r = spi.xfer2([1,(8+adcnum)<<4,0])
        adcout = ((r[1]&3) << 8) + r[2]
        return adcout

def readvoltage():
	# by default, voltage sensor is connected to adc channel 0
	v_adc = readadc(0)
	# max adc value is 1023
	# the reference voltage is assumed to be 3.3 V
	# the voltage "Sensor" divides actual voltage by 5
	voltage = (v_adc/1023.0)*3.3*5.0
	return voltage

while True:
        print "Voltage = ", readvoltage(), " V"
        time.sleep(1)

