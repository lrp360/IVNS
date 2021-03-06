from components.base.ecu.software.abst_comm_layers import AbstractCommModule
from tools.general import RefList, General as G
from io_processing.surveillance_handler import MonitorInput, MonitorTags
from components.base.ecu.software.impl_physical_layers import StdPhysicalLayer
from components.base.ecu.software.impl_datalink_layers import StdDatalinkLayer
from components.base.ecu.software.impl_transport_layers import FakeSegmentTransportLayer,\
    SegmentTransportLayer


class MyProtocolCommModule(AbstractCommModule):
    
    def __init__(self, sim_env, ecu_id):
        ''' Constructor
            
            Input:  ecu_id         string                   id of the corresponding AbstractECU
                    sim_env        simpy.Environment        environment of this component
            Output:  -
        '''
        AbstractCommModule.__init__(self, sim_env)

        # local parameters
        self._ecu_id = ecu_id
        self._jitter_in = 1
        self.monitor_list = RefList()
        
        # initialize
        self._init_layers(self.sim_env, self.MessageClass)
    
    def receive_msg(self):
        ''' receives messages via the tesla mechanism after
            they where authenticated. Then messages that were 
            authenticated are buffered in _messages_to_return
            and returned to higher layers sequentially on each 
            call of this method
            
            Input:     -
            Output:    message_data    object/string/...    message that was received
                       message_id      integer              id of received message
                       
            NOTE: 
                Accessing sender of a message 
                    -> USE: message_data.sender_id
                Accessing message_id of the received message 
                    -> USE: message_id
                Accessing message content
                    -> USE: message_data.get()
                
                message_data is of type SegData                
        '''

        while True:
                        
            # receive from lower layer
            [message_id, message_data] = yield self.sim_env.process(self.transp_lay.receive_msg())        
            
            # do something here e.g. if message_id = Handshake request received here, 
            # -> send something as response e.g. 
            # PLACE CODE HERE
            print("\n\nRECEIVER\nTime: "+str(self.sim_env.now)+"--Communication Layer: \nI am ECU " + self._ecu_id + "\nReceived message:\n - ID: " + str(message_id) +"\n - Content: " + message_data.get())
        
        # push to higher layer
        return [message_id, message_data]

    def send_msg(self, sender_id, message_id, message):
        ''' this  method receives the message from the application
            layer and transmits it further to the transport layer
            or if required handles the security communication

            Input:  sender_id    string        ID of the ECU that wants to send the message
                    message_id   integer       identifier of the message that is to be sent
                    message      object        message that will be sent
            Output: -
        '''        
        # do something with received message
        # PLACE CODE HERE        
        print("\n\nSENDER - \nTime: "+str(self.sim_env.now)+"--Communication Layer: \nI am ECU " + sender_id + "\nSending message:\n - ID: " + str(message_id)+"\n - Content: " + message.get())
        
        # Send message - here send your message with your message_id
        yield  self.sim_env.process(self.transp_lay.send_msg(sender_id, message_id, message))

            
    def _init_layers(self, sim_env, MessageClass):
        ''' Initializes the software layers 
            
            Input:  sim_env                        simpy.Environment        environment of this component                      
                    MessageClass                   AbstractBusMessage       class of the messages  how they are sent on the CAN Bus
            Output: -                   
        '''
        
        # create layers
        self.physical_lay = StdPhysicalLayer(sim_env)         
        self.datalink_lay = StdDatalinkLayer(sim_env) 
        self.transp_lay = SegmentTransportLayer(sim_env, MessageClass)
   
        # interconnect layers             
        self.datalink_lay.physical_lay = self.physical_lay        
        self.transp_lay.datalink_lay = self.datalink_lay           
        
        
    @property
    def ecu_id(self):
        return self._ecu_id
               
    @ecu_id.setter    
    def ecu_id(self, value):
        self._ecu_id = value          

    def monitor_update(self):
        ''' updates the monitor connected to this ecu
            
            Input:    -
            Output:   monitor_list    RefList    list of MonitorInputs
        '''
        items_1 = len(self.transp_lay.datalink_lay.controller.receive_buffer.items)
        items_2 = self.transp_lay.datalink_lay.transmit_buffer_size
        
        G().mon(self.monitor_list, MonitorInput(items_1, MonitorTags.BT_ECU_RECEIVE_BUFFER, self._ecu_id, self.sim_env.now))
        G().mon(self.monitor_list, MonitorInput(items_2, MonitorTags.BT_ECU_TRANSMIT_BUFFER, self._ecu_id, self.sim_env.now))
        
        self.monitor_list.clear_on_access()  # on the next access the list will be cleared        
        return self.monitor_list.get()

