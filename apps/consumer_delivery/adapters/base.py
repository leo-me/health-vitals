from abc import ABC, abstractmethod
from typing import Any


class IConsumerAdapter(ABC):

  name: str = ''

  # meta: get_format get_schema
  # process data: validate, transform, deliver
  # availability: is_available
  # handle error:  on_error

  # @abstractmethod
  # def get_name(self) -> str:
  #   """Return the adapter name. """
  #   ...

  @abstractmethod
  def get_format(self) -> str:
    """Return the output format identifier, e.g. 'json', 'csv', 'webhook'. """
    ...

  @abstractmethod
  def get_schema(self) -> object:
    """Return the output object"""
    ...

  @abstractmethod
  def validate(self, data: Any) -> None:
    """Check if the data is valid."""
    ...

  @abstractmethod
  def transform(self, data: Any) -> None:
    """ Processed health data."""
    ...


  @abstractmethod
  def deliver(self, data: Any) -> None:
    """Deliver processed health insight to the consumer."""
    ...

  @abstractmethod
  def is_available(self, data: Any) -> None:
    """check if the adapter works"""
    ...

  @abstractmethod
  def on_error(cls, subclass):
    """handle error"""

