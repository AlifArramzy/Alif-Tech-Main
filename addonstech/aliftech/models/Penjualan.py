from odoo import api, fields, models
from odoo.exceptions import UserError, ValidationError


class Penjualan(models.Model):
    _name = 'aliftech.penjualan'
    _description = 'Penjualan'

    name = fields.Char(string='No. Nota')
    nama_pembeli = fields.Char(string='Nama Pembeli')
    # id_member = fields.Char(
    #     compute="_compute_id_member",
    #     string='Id_member',
    #     required=False)
    tgl_penjualan = fields.Datetime(
        string='Tanggal Transaksi',
        default=fields.Datetime.now())
    total_bayar = fields.Integer(
        string='Total Pembayaran',
        compute='_compute_totalbayar')
    detailpenjualan_ids = fields.One2many(
        comodel_name='aliftech.detailpenjualan',
        inverse_name='penjualan_id',
        string='Detail Penjualan')
    state = fields.Selection(
        string='Status',
        selection=[('draft', 'Draft'),
                   ('confirm', 'Confirm'),
                   ('done', 'Done'),
                   ('cancelled', 'Cancelled'),
                   ],
        required=True, readonly=True, default='draft')

    # @api.depends('nama_pembeli')
    # def _compute_id_member(self):
    #     for rec in self:
    #         rec.id_member = rec.nama_pembeli.id_member

    def action_confirm(self):
        self.write({'state': 'confirm'})
    def action_done(self):
        self.write({'state': 'done'})
    def action_cancel(self):
        self.write({'state': 'cancelled'})
    def action_draft(self):
        self.write({'state': 'draft'})

    @api.depends('detailpenjualan_ids')
    def _compute_totalbayar(self):
        for rec in self:
            result = sum(self.env['aliftech.detailpenjualan'].search(
                [('penjualan_id', '=', rec.id)]).mapped('subtotal'))
            rec.total_bayar = result

    @api.ondelete(at_uninstall=False)
    def __ondelete_penjualan(self):
        if self.detailpenjualan_ids:
            a = []
            for rec in self:
                a = self.env['aliftech.detailpenjualan'].search([('penjualan_id','=',rec.id)])
                print(a)
            for ob in a:
                print(str(ob.produk_id.name) + ' ' + str(ob.qty))
                ob.produk_id.stok += ob.qty

    # def unlink(self):
    #     if self.detailpenjualan_ids:
    #         a = []
    #         for rec in self:
    #             a = self.env['aliftech.detailpenjualan'].search([('penjualan_id','=',line.id)])
    #             print(a)
    #         for ob in a:
    #             print(str(ob.produk_id.name) + ' ' + str(ob.qty))
    #             ob.produk_id.stok += ob.qty

    #     record = super(Penjualan,self).unlink()

    def write(self, vals):
      for rec in self:
          a = self.env['aliftech.detailpenjualan'].search([('penjualan_id','=',rec.id)])
          print(a)
          for data in a:
              print(str(data.produk_id.name)+' '+str(data.qty)+' '+str(data.produk_id.stok))
              data.produk_id.stok += data.qty   
      record = super(Penjualan, self).write(vals)    
      for rec in self:
          b = self.env['aliftech.detailpenjualan'].search([('penjualan_id','=',rec.id)])
          print(a)
          print(b)
          for databaru in b:
              if databaru in a:
                  print(str(databaru.produk_id.name)+' '+str(databaru.qty)+' '+str(databaru.produk_id.stok))
                  databaru.produk_id.stok -= databaru.qty
              else:
                  pass
      return record

    _sql_constraints = [
        ('no_nota_unik','unique (name)','Nomor Nota yang di input tidak boleh sama!')
    ]

class DetailPenjualan(models.Model):
    _name = 'aliftech.detailpenjualan'
    _description = 'Detail'

    name = fields.Char(string='Nama')
    penjualan_id = fields.Many2one(
        comodel_name='aliftech.penjualan',
        string='Detail Penjualan')
    produk_id = fields.Many2one(
        comodel_name='aliftech.produk',
        string='List Produk')
    harga_satuan = fields.Integer(
        string='Harga Satuan',
        onchange='_onchange_produk_id')
    qty = fields.Integer(string='Quantity')
    subtotal = fields.Integer(compute='_compute_subtotal', string='Subtotal')

    @api.depends('harga_satuan', 'qty')
    def _compute_subtotal(self):
        for line in self:
            line.subtotal = line.qty * line.harga_satuan

    @api.onchange('produk_id')
    def _onchange_produk_id(self):
        if self.produk_id.harga_jual:
            self.harga_satuan = self.produk_id.harga_jual

    @api.model
    def create(self, vals):
        record = super(DetailPenjualan, self).create(vals)
        if record.qty:
            self.env['aliftech.produk'].search([('id','=',record.produk_id.id)]
            ).write({'stok': record.produk_id.stok - record.qty})
        return record

    @api.constrains('qty')
    def check_quantity(self):
        for rec in self:
            if rec.qty <1:
                raise ValidationError("Mohon diisi berapa banyak {} yang anda ingin beli.".format(rec.produk_id.name))
            elif (rec.produk_id.stok < rec.qty):
                raise ValidationError('Permintaan anda melebihi jumlah stok {} yang ada, hanya tersedia {}'.format(rec.produk_id.name,rec.produk_id.stok))
