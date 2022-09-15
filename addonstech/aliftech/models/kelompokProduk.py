from odoo import api, fields, models


class KelompokProduk(models.Model):
    _name = 'aliftech.kelompokproduk'
    _description = 'New Description'

    name = fields.Selection([
        ('gpu', 'GPU'),
        ('cpu', 'CPU'),
        ('ram', 'RAM'),
        ('ssd', 'SSD'),
        ('hdd', 'HDD')
    ], string='Nama Kelompok')

    #name = fields.Char(string='Nama Kelompok Produk')
    kode_kelompok = fields.Char(string='Kode Kelompok Produk')
    kode_rak = fields.Char(string='Kode Rak')
    produk_ids = fields.One2many(comodel_name='aliftech.produk',
                                inverse_name='kelompokproduk_id',
                                string='Daftar Produk')
    jml_item = fields.Char(compute='_compute_jml_item', string='Jml Item')
    daftar = fields.Char(string='Daftar isi')

    @api.onchange('name')
    def _onchange_kode_kelompok(self):
        if self.name == 'gpu':
            self.kode_kelompok = 'GPU01'
        elif self.name == 'cpu':
            self.kode_kelompok = 'CPU01'
        elif self.name == 'ram':
            self.kode_kelompok = 'RAM01'
        elif self.name == 'ssd':
            self.kode_kelompok = 'SSD01'
        elif self.name == 'hdd':
            self.kode_kelompok = 'HDD01'

    @api.depends('produk_ids')
    def _compute_jml_item(self):
        for record in self:
            a = self.env['aliftech.produk'].search([('kelompokproduk_id', '=', record.id)]).mapped('name')
            b = len(a)
            record.jml_item = b
            record.daftar = a
