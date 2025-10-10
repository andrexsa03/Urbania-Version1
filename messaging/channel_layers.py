"""
Channel layer configuration for development without Redis
"""

from channels.layers import InMemoryChannelLayer


class DevelopmentChannelLayer(InMemoryChannelLayer):
    """
    Channel layer en memoria para desarrollo
    Útil cuando Redis no está disponible
    """
    
    def __init__(self, expiry=60, capacity=100, **kwargs):
        super().__init__(expiry=expiry, capacity=capacity, **kwargs)
        
    async def group_add(self, group, channel):
        """Agregar canal a un grupo"""
        await super().group_add(group, channel)
        
    async def group_discard(self, group, channel):
        """Remover canal de un grupo"""
        await super().group_discard(group, channel)
        
    async def group_send(self, group, message):
        """Enviar mensaje a todos los canales en un grupo"""
        await super().group_send(group, message)