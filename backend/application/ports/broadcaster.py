"""
Port: IBroadcaster
Puerto abstracto para la difusión de eventos y sincronización en tiempo real.
Author: Hugo Francisco Luis Inclan
Copyright (c) 2026 Hugo Francisco Luis Inclan
"""

from abc import ABC, abstractmethod
from typing import Any
from domain.entities import RadioBroadcastMessage


class IBroadcaster(ABC):
    """Contrato del puerto para difusión de mensajes a clientes conectados."""

    @abstractmethod
    async def connect(self, client: Any) -> None:
        """Registra un nuevo cliente conectado al canal."""
        pass

    @abstractmethod
    def disconnect(self, client: Any) -> None:
        """Remueve a un cliente desconectado del canal."""
        pass

    @abstractmethod
    async def broadcast(self, message: RadioBroadcastMessage) -> None:
        """Difunde un mensaje de estado a todos los clientes activos."""
        pass

    @property
    @abstractmethod
    def listeners_count(self) -> int:
        """Cantidad de oyentes conectados activamente."""
        pass
