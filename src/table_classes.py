from sqlalchemy import Column, BigInteger, Integer, Boolean, String, Text, DateTime, ForeignKey
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import relationship

Base = declarative_base()

"""The following classes declare the tables of a database"""

class DbInformation(Base):
   __tablename__ = 'DB_INFORMATION'
   db_name = Column(String, primary_key = True)
   db_date_created = Column(DateTime)
   db_date_modified = Column(DateTime)
   db_version = Column(Integer)
   db_last_scan_id = Column(Integer)


class ScanCode(Base):
   __tablename__ = 'SCAN_CODE'
   scan_return_code = Column(Integer, primary_key = True)
   scan_return_code_description = Column(String)

   scans = relationship("Scan", back_populates="scan_code")


class Scan(Base):
   __tablename__ = 'SCAN'
   scan_id = Column(Integer, primary_key = True)
   scan_hostname = Column(String)
   scan_date = Column(DateTime)
   scan_return_code = Column(Integer, ForeignKey('SCAN_CODE.scan_return_code'))

   scan_code = relationship("ScanCode", back_populates="scans")
   files = relationship("File", back_populates="scan")


class Origin(Base):
   __tablename__ = 'ORIGIN'
   origin_id = Column(Integer, primary_key = True)
   origin_is_local_flag = Column(Boolean)
   origin_url_or_hostname = Column(String)
   origin_retrival_datetime = Column(DateTime)

   files = relationship("File", back_populates="origin")


class File(Base):
   __tablename__ = 'FILE'
   file_id = Column(Integer, primary_key = True)
   scan_id = Column(Integer, ForeignKey('SCAN.scan_id'))
   file_name = Column(String)
   file_extension = Column(String)
   file_path = Column(String)
   file_size = Column(BigInteger)
   file_date_created = Column(DateTime)
   file_date_modified = Column(DateTime)
   swh_known = Column(Boolean)
   file_updated = Column(Boolean)
   origin_id = Column(Integer, ForeignKey('ORIGIN.origin_id'))

   scan = relationship("Scan", back_populates="files")
   origin = relationship("Origin", back_populates="files")


class Hash(Base):
   __tablename__ = 'HASH'
   hash_id = Column(Integer, primary_key = True)
   hash_value = Column(String)
   hash_function_name = Column(String, ForeignKey('HASH_FUNCTION.hash_function_name'))
   file_id = Column(Integer, ForeignKey('FILE.file_id'))

   hash_function = relationship("HashFunction", back_populates="hashes")


class HashFunction(Base):
   __tablename__ = 'HASH_FUNCTION'
   hash_function_name = Column(String, primary_key = True)
   hash_function_fuzzy_flag = Column(Boolean)
   hash_function_size = Column(Integer)

   hashes = relationship("Hash", back_populates="hash_function")