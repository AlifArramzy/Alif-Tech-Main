from crypt import methods
from odoo import http, models, fields
from odoo.http import request
import json

class Aliftech(http.Controller):
    @http.route('/aliftech/getproduk', auth='public', method=['GET'])
    def getProduk(self, **kw):
        produk = request.env['aliftech.produk'].search([])
        isi = []
        for bb in produk:
            isi.append({
                'nama_produk': bb.name,
                'harga_jual': bb.harga_jual,
                'stok': bb.stok
            })       
        return json.dumps(isi)

    @http.route('/aliftech/getsupplier', auth='public', method=['GET'])
    def getSupplier(self, **kw):
        supplier = request.env['aliftech.supplier'].search([])
        sup = []
        for s in supplier:
            sup.append({
                'nama_perusahaan': s.name,
                'alamat': s.alamat,
                'no_telepon': s.no_telp,
                'produk_id': s.produk_id[0].name
            })    
        return json.dumps(sup)