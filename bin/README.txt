
Compute extinction correction for COADD_OBJECTS table
-----------------------------------------------------

To compute for all objects in: Y1P1_COADD
%> compute_SFD98_coadd_objects.py --CoaddVersion Y1P1_COADD

For one tile
%> compute_SFD98_coadd_objects.py Y1P1_COADD --TileName DES2242-0041 --TableName felipe.coadd_objects_xcorr --CreateTable

For all tiles in Y1A1_COADD_STRIPE82
%> compute_SFD98_coadd_objects.py Y1A1_COADD_STRIPE82 --TableName felipe.coadd_objects_xcorr --CreateTable

For all tiles in Y1A1_COADD_SPT
%> compute_SFD98_coadd_objects.py Y1A1_COADD_SPT felipe.coadd_xcorr_Y1A1_COADD_SPT --CreateTable

Compute extinction correction for catalogs fits table file
-----------------------------------------------------------

Computes SFD98 Galactic extinction from a SExtractor file
%> compute_SFD98_coadd_catalog.py CatName OutName


To create a new db table in desoper manually (not needed anymore)
-------------------------------------------------------------------

1) mydesoper 
2) SQL> @felipe.coadd_objects_xcorr.sql
grant select on coadd_objects_xcorr to des_reader; 

To create a new db table in desoper

1) mydessci
2) SQL> @felipe.sva1_coadd_objects_xcorr.sql

