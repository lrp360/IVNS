from components.base.ecu.types.impl_ecu_simple import SimpleECU
from components.base.ecu.software.ecu_software import ECUSoftware
from components.security.ecu.software.impl_app_layer_secure import SecureApplicationLayer
from layers.impl_comm_module_my_protocol import MyProtocolCommModule

class MyProtocolECU(SimpleECU):

    def __init__(self, sim_env=None, ecu_id=None, data_rate=None, size_sending_buffer=None, size_receive_buffer=None):
        ''' Constructor
        
            Input:  sim_env                simpy.Environment        environment in which this ECU lives
                    ecu_id                 string                   id of this ECU component 
                    data_rate              integer                  data_rate of the connected bus
                    size_sending_buffer    float                    size of the sending buffer of this ECU
                    size_receive_buffer    float                    size of the receiving buffer of this ECU   
            Output: -
        '''
        
        # set settings
        self.set_settings()
        if sim_env == None: return  
        
        # set SW and HW
        SimpleECU.__init__(self, sim_env, ecu_id, data_rate, size_sending_buffer, size_receive_buffer)                
        self.ecuSW = ECUSoftware(sim_env, MyProtocolCommModule(sim_env, ecu_id), SecureApplicationLayer(sim_env, ecu_id))
        
        # connect
        self._connect_hw_sw()                
       
     
    def add_sending(self, start_time, interval, message_id, data, data_len):
        ''' this method adds a new sending action to the application layer of this 
            ECU. Then the message will start sending messages in the defined interval
            starting at the specified start_time
            
            Input:  start_time    float            time at which the first message is sent
                    interval      float            period within which the messages are sent
                    message_id    integer          message identifier of the messages that are sent
                    data          object/..        content of the messages that are sent
                    data_length   float            size of one message
            Output: -        
        '''
        self.ecuSW.app_lay.add_sending(start_time, interval, message_id, data, data_len)
        
    
    def get_type_id(self):
        ''' returns the id of this ECU type
        
            Input:    -
            Output:   ecu_type    string    type of this ECU; e.g.'TLSECU'
        '''
        return "MyProtocolECU"
    
    
    def add_stream(self, new_stream):
        ''' this method adds a new stream that is allowed to the TESLA environment.
            This stream will then be legal and the ECUs will send according to those
            streams.
            
            Input:    new_stream    MessageStream    message stream that is added to the environment
            Output:   -
        '''
        # push to communication module
        self.ecuSW.comm_mod.add_stream(new_stream)

        # add HW filter
        if self.ecu_id in new_stream.receivers and \
           new_stream.message_id not in self._allowed_streams:
            self._allowed_streams += [new_stream.message_id]
            self.ecuHW.transceiver.install_filter(self._allowed_streams)

    def set_max_message_number(self, nr_messages):
        ''' sets the number of messages that are sent by this ecu per
            stream

            Input:    nr_messages    int    number of messages sent
            Output:    -
        '''
        self.ecuSW.app_lay.set_max_message_number(nr_messages)
    
    def set_settings(self):
        ''' sets the initial setting association between the settings variables
            and the actual parameter
        
            Input:   -
            Output:  -
        '''
        self.settings = {}
        
        return self.settings
        
    
    def monitor_update(self):
        ''' returns a list of monitor inputs
            
            Input:    -
            Output:   list    list    list of MonitorInput objects
        '''
        return self.ecuSW.comm_mod.monitor_update()


'''class StdTLSECUTimingFunctions(object):

    def __init__(self, main_library_tag='CyaSSL'):
        self.available_tags = ['CyaSSL', 'Crypto_Lib_HW', 'Crypto_Lib_SW']

        self.library_tag = main_library_tag  # e.g. CyaSSL, or CryptoLib

        self.function_map = {}
            
        # Record Layer
        self.function_map['t_tls_record_compression'] = self.c_t_tls_record_compression
        self.function_map['t_tls_record_decompression'] = self.c_t_tls_record_decompression
         
    
    
    def get_function_map(self):

        return self.function_map

    
    def c_t_timing_function_1(self, msg_size, compr_alg):
        if compr_alg == CompressionMethod.NULL:
            return 0        
        return 0
    
    
    def c_t_timing_function_2(self, compressed_msg_size, compr_alg):
        if compr_alg == CompressionMethod.NULL:
            return 0     
        return 0
'''