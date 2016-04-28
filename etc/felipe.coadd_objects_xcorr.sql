-- make sure we delete before we created
drop   table felipe.coadd_objects_xcorr purge;
create table felipe.coadd_objects_xcorr (
COADD_OBJECTS_ID        NUMBER(11)  NOT NULL,
XCORR_SFD98_G           NUMBER(10,6),
XCORR_SFD98_R           NUMBER(10,6),
XCORR_SFD98_I           NUMBER(10,6),
XCORR_SFD98_Z           NUMBER(10,6),
XCORR_SFD98_Y           NUMBER(10,6),
eBV                     NUMBER(10,6),
L                       BINARY_FLOAT,
B                       BINARY_FLOAT,
TILENAME                VARCHAR2(20),
constraint coadd_objects_xcorr_pk PRIMARY KEY (coadd_objects_id)
-- constraint coadd_objects_xcorr_fk FOREIGN KEY (id) REFERENCES DES_ADMIN.coadd_objects(COADD_OBJECTS_ID)
);

-- Add description of columns
comment on column coadd_objects_xcorr.COADD_OBJECTS_ID is 'ID from COADD_OBJECTS table';
comment on column coadd_objects_xcorr.XCORR_SFD98_G    is 'g-band Galactic extinction Correction from SFD98 and Rv=3.1';
comment on column coadd_objects_xcorr.XCORR_SFD98_R    is 'r-band Galactic extinction Correction from SFD98 and Rv=3.1';
comment on column coadd_objects_xcorr.XCORR_SFD98_I    is 'i-band extinction Correction from SFD98 and Rv=3.1';
comment on column coadd_objects_xcorr.XCORR_SFD98_Z    is 'z-band extinction Correction from SFD98 and Rv=3.1';
comment on column coadd_objects_xcorr.XCORR_SFD98_Y    is 'Y-band extinction Correction from SFD98 and Rv=3.1';
comment on column coadd_objects_xcorr.eBV              is 'e(B-V) extinction';
comment on column coadd_objects_xcorr.L                is 'Galactic Longitude';
comment on column coadd_objects_xcorr.B                is 'Galactic Latitude';
comment on column coadd_objects_xcorr.TILENAME         is 'DES parent tilename';


