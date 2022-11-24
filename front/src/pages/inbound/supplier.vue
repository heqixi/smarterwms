<template>
  <div class="q-pt-sm">
    <transition appear enter-active-class="animated fadeIn">
      <CommonTable
        ref="supplierTable"
        :table_list="table_list"
        :rowKey="rowKey"
        :columns="columns"
        :numRows="numRows"
        :loading="loading"
        :topButtons="topButtons"
        :filterFn="filteredRows"
        :getNextPage="getListNext"
        :searchFn="getSearchList"
        @refresh="refresh"/>
    </transition>
  </div>
</template>
<router-view/>

<script>
import { getauth, postauth, deleteauth, getfile, putauth } from 'boot/axios_request'
import { date, exportFile, LocalStorage } from 'quasar'
import CommonTable from '../../components/Share/commontable.vue'
import GoodsSearch from 'pages/order/components/goodssearch'
import GoodsSearchForSupplier from 'src/pages/inbound/components/goodsSearchForSupplier'
import NewFormDialog from 'components/Share/newFormDialog'

export default {
  name: 'Pagesupplier',
  data () {
    var _this = this
    return {
      openid: '',
      login_name: '',
      authin: '0',
      rowKey: 'id',
      numRows: 0,
      supplierForm: {
        supplier_name: '',
        supplier_city: '',
        supplier_address: '',
        supplier_contact: '',
        supplier_manager: '',
        supplier_level: 1
      },
      purchaseFormData: {
        tag: '',
        url: '',
        supplier: '',
        price: '',
        image_url: ''
      },
      newDataDialog: false,
      newFormItems: [],
      onNewDataSummit: undefined,
      onNewDataCancel: undefined,
      newFormData: {},
      pathname: 'supplier/',
      pathname_previous: '',
      pathname_next: '',
      separator: 'cell',
      loading: false,
      height: '',
      table_list: [],
      topButtons: [
        {
          name: 'new',
          label: '新增',
          tip: '新增库存记录',
          icon: 'add',
          click: () => {
            _this.$q.notify({
              message: '新增库存功能未实现',
              icon: 'close',
              color: 'negative'
            })
          }
        },
        {
          name: 'confirm',
          label: '新增购买链接',
          tip: '供应商新增购买链接',
          click: supplier => {
            _this.newOrEditPurchasePlan()
          }
        }
      ],
      columns: [
        {
          name: 'supplier_name',
          label: '供应商',
          align: 'center',
          type: 'text',
          field: 'supplier_name',
          style: { width: '150px', maxWidth: '150px', whiteSpace: 'normal'}
        },
        {
          name: 'supplier_city',
          label: '所在城市',
          align: 'center',
          type: 'text',
          field: 'supplier_city',
          style: { width: '100px', maxWidth: '100px', whiteSpace: 'normal' }
        },
        {
          name: 'supplier_contact',
          label: '联系方式',
          align: 'center',
          type: 'text',
          field: 'supplier_contact',
          style: { width: '100px', maxWidth: '100px', whiteSpace: 'normal' }
        },
        {
          name: 'supplier_purchases',
          label: '购买链接',
          field: 'supplier_purchases',
          align: 'center',
          type: 'table',
          keepExpand: true,
          rowHeight: 50,
          class: 'col-5',
          subColumns: [
            {
              name: 'image_url',
              label: '图片',
              field: 'image_url',
              type: 'image',
              class: 'col-2'
            },
            {
              name: 'tag',
              label: '标签',
              field: 'tag',
              class: 'col-4'
            },
            {
              name: 'price',
              label: '价格',
              field: 'price',
              class: 'col-1'
            },
            {
              name: 'url',
              label: '链接',
              type: 'url',
              field: 'url',
              class: 'col-1'
            },
            {
              name: 'action',
              label: this.$t('action'),
              type: 'actions',
              class: 'col-4',
              align: 'center',
              actions: [
                {
                  name: 'addGoods',
                  label: '产品',
                  tip: '查看链接供应产品',
                  click: (supplier, purchase) => {
                    console.log('add goods, ', supplier, purchase)
                    _this.viewGoodsOfPurchasePlan(supplier, purchase)
                  }
                },
                {
                  name: 'edit',
                  label: '编辑',
                  tip: '编辑这条数据',
                  click: (supplier, purchase) => {
                    console.log('delete purchase, ', supplier, purchase)
                    _this.newOrEditPurchasePlan(supplier, purchase)
                  }
                },
                {
                  name: 'delete',
                  label: '删除',
                  tip: '删除这条数据',
                  click: (supplier, purchase) => {
                    console.log('delete purchase, ', supplier, purchase)
                    _this.deletePurchasePlan(supplier, purchase)
                  }
                }
              ]
            }
          ]
        },
        {
          name: 'creater',
          label: this.$t('creater'),
          type: 'text',
          field: 'creater',
          align: 'center',
          class: 'col-1'
        },
        {
          name: 'action',
          label: this.$t('action'),
          class: 'col-2',
          type: 'actions',
          style: {
            width: '100px',
            textAlign: 'center',
            whiteSpace: 'normal',
            fontSize: '8px'
          },
          align: 'center',
          actions: [
            {
              name: 'delete',
              label: '删除',
              tip: '删除供应商',
              click: (supplier) => {
                _this.deleteSupplier(supplier)
              }
            }
          ]
        }
      ],
      filter: '',
      pagination: {
        page: 1,
        rowsPerPage: '30'
      },
      newForm: false,
      editid: 0,
      editFormData: {},
      editMode: false,
      deleteForm: false,
      deleteid: 0,
      error1: this.$t('baseinfo.view_supplier.error1'),
      error2: this.$t('baseinfo.view_supplier.error2'),
      error3: this.$t('baseinfo.view_supplier.error3'),
      error4: this.$t('baseinfo.view_supplier.error4'),
      error5: this.$t('baseinfo.view_supplier.error5'),
      error6: this.$t('baseinfo.view_supplier.error6')
    }
  },
  methods: {
    async viewGoodsOfPurchasePlan (supplier, purchasePlan) {
      const _this = this
      if (!purchasePlan.goods) {
        purchasePlan.goods = await getauth(_this.pathname + `purchase/goods?id=${purchasePlan.id}`)
      }
      const goodsParams = purchasePlan.goods.join('&id_in=')
      const goodsIds = purchasePlan.goods
      let path = 'goods/?group=true'
      if (goodsParams) {
        path += `&id_in=${goodsParams}`
      }
      const dialog = _this.$q.dialog({
        component: GoodsSearchForSupplier,
        path: path,
        refName: 'viewDataDialog',
        searchPath: 'goods/?purchases=details',
        defaultSelected: goodsIds,
        additionalTopButtons: [
          {
            name: '移除',
            label: '移除产品',
            tip: '移除产品',
            click: selectedGoods => {
              console.log('selectedList, ', selectedGoods.length)
              if (selectedGoods.length <= 0) {
                _this.$q.notify({
                  message: '请选择需要移除的产品',
                  icon: 'close',
                  color: 'negative'
                })
              }
              const goods2Remove = selectedGoods.filter(goods => {
                return purchasePlan.goods.find(goodsId => { return goodsId === goods.id }) !== undefined
              })
              if (goods2Remove.length > 0) {
                console.log('remove goods of purchase ', goods2Remove)
                const formData = {
                  id: purchasePlan.id,
                  goods: goods2Remove.map(goods => goods.id),
                  remove: true
                }
                putauth('supplier/purchase/' + purchasePlan.id + '/', formData).then(res => {
                  console.log('remove goods to purchase success ', res)
                  _this.refresh()
                })
                dialog.hide()
              }
            }
          }
        ]
      }).onOk(operation => {
        console.log('selected goods on ok ', operation.goods)
        _this.addGoodsToPurchaseRemote(operation.goods, purchasePlan)
      })
    },
    addGoodsToPurchaseRemote (selectedGoods, purchasePlan) {
      const goods2Add = selectedGoods.filter(goods => {
        return purchasePlan.goods.find(goodsId => { return goodsId === goods.id }) === undefined
      })
      if (goods2Add.length > 0) {
        const formData = {
          id: purchasePlan.id,
          goods: goods2Add.map(goods => goods.id),
          add: true
        }
        putauth('supplier/purchase/' + purchasePlan.id + '/', formData).then(res => {
          console.log('add goods to purchase success ', res)
          goods2Add.forEach(goods => { purchasePlan.goods.unshift(goods.id) })
          console.log(purchasePlan.goods)
        })
      } else {
        console.log('no goods need to be add to purchase plan')
      }
    },
    // addGoodsToPurchasePlan (supplier, purchasePlan) {
    //   var _this = this
    //   _this.$q.dialog({
    //     component: GoodsSearchForSupplier,
    //     refName: 'addGoodsDialog'
    //   }).onOk(selectedGoods => {
    //     console.log('add goods to purchase plan on ok', selectedGoods)
    //     if (selectedGoods.length <= 0) {
    //       _this.$q.notify({
    //         message: '你似乎没有选择任何商品',
    //         icon: 'close',
    //         color: 'negative'
    //       })
    //       return
    //     }
    //     const goods2Add = selectedGoods.filter(goods => {
    //       return purchasePlan.goods.find(goodsId => { return goodsId === goods.id }) === undefined
    //     })
    //     if (goods2Add.length <= 0) {
    //       _this.$q.notify({
    //         message: '无须重复添加产品',
    //         icon: 'close',
    //         color: 'negative'
    //       })
    //       return
    //     }
    //     const formData = {
    //       id: purchasePlan.id,
    //       goods: goods2Add.map(goods => goods.id),
    //       add: true
    //     }
    //     putauth('supplier/purchase/' + purchasePlan.id + '/', formData).then(res => {
    //       console.log('add goods to purchase success ', res)
    //     })
    //   })
    // },
    deleteSupplier (supplier) {
      console.log('deleteSupplier ', supplier)
      var _this = this
      deleteauth('supplier/' + supplier.id + '/', {}).then(res => {
        console.log('delete purchase plan success ', res)
        for (var i = 0; i < _this.table_list.length; i++) {
          if (_this.table_list[i].id === supplier.id) {
            _this.table_list.splice(i, 1)
          }
        }
      }).catch(err => {
        _this.$q.notify({
          message: '删除失败',
          icon: 'close',
          color: 'negative'
        })
      })
    },
    deletePurchasePlan (supplier, puchasePlan) {
      console.log('deletePurchasePlan ', puchasePlan)
      var _this = this
      deleteauth('supplier/purchase/' + puchasePlan.id + '/', {}).then(res => {
        console.log('delete purchase plan success ', res)
        if (res.status === 200) {
          const purchases = supplier.supplier_purchases
          for (var i = 0; i < purchases.length; i++) {
            if (purchases[i].id === puchasePlan.id) {
              purchases.splice(i, 1)
            }
          }
        } else {
          _this.$q.notify({
            message: '删除失败',
            icon: 'close',
            color: 'negative'
          })
        }
      })
    },
    newOrEditPurchasePlan (supplier, purchasePlan) {
      console.log('new or edit purchase plan ', purchasePlan)
      var _this = this
      _this.purchaseFormData.tag = purchasePlan ? purchasePlan.tag : ''
      _this.purchaseFormData.url = purchasePlan ? purchasePlan.url : ''
      _this.purchaseFormData.supplier = supplier || undefined
      _this.purchaseFormData.price = purchasePlan ? purchasePlan.price : ''
      _this.purchaseFormData.image_url = purchasePlan ? purchasePlan.image_url : ''
      const purchaseFormItems = [
        {
          name: 'supplier',
          label: '选择或新增供应商',
          type: 'select',
          field: 'supplier',
          options: _this.table_list,
          optionLabel: supplier => {
            return supplier.supplier_name
          },
          newValue: () => {
            _this.newSupplier()
              .then(supplier => {
                _this.table_list.unshift(supplier)
                _this.purchaseFormData.supplier = supplier
              }).catch(err => {
                console.log('handlerNewSupplier new supplier fail', err)
              })
          }
        },
        {
          name: 'tag',
          label: '标签',
          field: 'tag',
          edit: true
        },
        {
          name: 'url',
          label: '采购链接',
          field: 'url',
          edit: true
        },
        {
          name: 'price',
          label: '价格',
          field: 'price',
          edit: true
        },
        {
          name: 'image_url',
          label: '图片链接',
          field: 'image_url',
          edit: true
        }
      ]
      this.$q.dialog({
        component: NewFormDialog,
        title: '请输入采购信息',
        newFormData: _this.purchaseFormData,
        newFormItems: purchaseFormItems
      }).onOk(() => {
        const formData = _this.purchaseFormData
        const planFormData = {
          creater: _this.login_name,
          openid: _this.openid,
          tag: formData.tag,
          supplier: formData.supplier.id,
          price: formData.price,
          url: formData.url,
          default: formData.default,
          id: purchasePlan ? purchasePlan.id : undefined,
          image_url: formData.image_url,
          partial: true
        }
        postauth('supplier/purchase/', planFormData)
          .then(savePurchasePlan => {
            console.log('new Purchase Plan save,', savePurchasePlan)
            this.$q.notify({
              message: '采购方案保存成功',
              icon: 'check',
              color: 'green'
            })
            purchasePlan.id = savePurchasePlan.id
            if (purchasePlan) {
              purchasePlan.tag = formData.tag
              purchasePlan.supplier = formData.supplier
              purchasePlan.url = formData.url
              purchasePlan.price = formData.price
              purchasePlan.image_url = formData.image_url
              if (planFormData.supplier !== supplier.id) {
                for (let i = 0; i < supplier.supplier_purchases.length; i++) {
                  if (supplier.supplier_purchases[i].id === purchasePlan.id) {
                    supplier.supplier_purchases.splice(i, 1)
                    break
                  }
                }
                const changeSupplier = _this.table_list.find(supplier => { return supplier.id === planFormData.supplier })
                if (changeSupplier) {
                  changeSupplier.supplier_purchases.unshift(planFormData)
                }
              }
            } else {
              _this.table_list.forEach(supplier => {
                // 把相加的采购链接加进供应商
                if (supplier.id === planFormData.supplier) {
                  console.log('add to supplier purchase plan ', supplier.supplier_purchases)
                  planFormData.goods = []
                  supplier.supplier_purchases.unshift(planFormData)
                }
              })
            }
          })
        // .catch(err => {
        //   this.$q.notify({
        //     message: '供应商保存失败',
        //     icon: 'close',
        //     color: 'negative'
        //   })
        // })
      })
    },
    newSupplier () {
      console.log('item new value ')
      var _this = this
      _this.supplierForm.supplier_name = ''
      _this.supplierForm.supplier_city = ''
      _this.supplierForm.supplier_address = ''
      _this.supplierForm.supplier_contact = ''
      _this.supplierForm.supplier_manager = ''
      _this.supplierForm.supplier_level = 1
      const supplierFormItems = [
        {
          name: 'supplier_name',
          label: '供应商名称',
          field: 'supplier_name',
          edit: true
        },
        {
          name: 'supplier_city',
          label: '所在城市',
          field: 'supplier_city',
          edit: true
        },
        {
          name: 'supplier_address',
          label: '详细地址',
          field: 'supplier_address',
          edit: true
        },
        {
          name: 'supplier_contact',
          label: '联系方式',
          field: 'supplier_contact',
          edit: true
        },
        {
          name: 'supplier_manager',
          label: '负责人',
          field: 'supplier_manager',
          edit: true
        }
      ]
      return new Promise((resolve, reject) => {
        _this.$q.dialog({
          component: NewFormDialog,
          title: '请输入供应商信息',
          newFormData: _this.supplierForm,
          newFormItems: supplierFormItems
        }).onOk(() => {
          const supplier = _this.supplierForm
          console.log('on new supplier summit ', supplier)
          supplier.creater = _this.login_name
          supplier.openid = _this.openid
          postauth('supplier/', supplier)
            .then(res => {
              console.log('save new supplier success response ', res)
              const supplierSave = res
              supplierSave.supplier_purchases = [] // 新建的供应商，供应商品为空
              this.$q.notify({
                message: '供应商保存成功',
                icon: 'check',
                color: 'green'
              })
              resolve(supplierSave)
            })
            .catch(err => {
              console.log('save new supplier fail ', err)
              this.$q.notify({
                message: '供应商保存失败',
                icon: 'close',
                color: 'negative'
              })
              reject('供应商保存失败')
            })
        })
      })
    },
    getList () {
      var _this = this
      if (LocalStorage.has('auth')) {
        getauth(_this.pathname + '?supplier_purchases=details', {}).then(res => {
          console.log('get  supplier', res)
          _this.table_list = res.results
          _this.pathname_previous = res.previous
          _this.pathname_next = res.next
        }).catch(err => {
          _this.$q.notify({
            message: err.detail,
            icon: 'close',
            color: 'negative'
          })
        })
      } else {
      }
    },
    filteredRows (supplier, searchTerm) {
      const nameMatch = supplier && supplier.supplier_name.indexOf(searchTerm) > -1
      let purchaseMatch = false
      let purchaseMatchCount = 0
      if (supplier.supplier_purchases) {
        for (let i = 0; i < supplier.supplier_purchases.length; i++) {
          const purchase = supplier.supplier_purchases[i]
          let match = false
          if (purchase.url && purchase.url === searchTerm) {
            match = true
            purchaseMatch = true
            purchaseMatchCount += 1
          }
          if (purchase.tag && purchase.tag === searchTerm) {
            match = true
            purchaseMatch = true
            purchaseMatchCount += 1
          }
          if (match) {
            supplier.supplier_purchases.splice(i, 1)
            supplier.supplier_purchases.unshift(purchase)
          }
        }
      }
      if (purchaseMatchCount > 0) {
        this.$q.notify({
          message: `匹配到 ${supplier.supplier_name} 的 ${purchaseMatchCount} 条购买链接, 位于供应商的前 ${purchaseMatchCount} 个`,
          icon: 'check',
          color: 'green'
        })
      }
      const match = nameMatch || purchaseMatch
      console.log('supplier filter ', match, supplier, searchTerm)
      return nameMatch || purchaseMatch
    },
    getSearchList () {
      // var _this = this
      // if (LocalStorage.has('auth')) {
      //   getauth(_this.pathname + '?supplier_name__icontains=' + _this.filter, {}).then(res => {
      //     _this.table_list = res.results
      //     _this.pathname_previous = res.previous
      //     _this.pathname_next = res.next
      //   }).catch(err => {
      //     _this.$q.notify({
      //       message: err.detail,
      //       icon: 'close',
      //       color: 'negative'
      //     })
      //   })
      // } else {
      // }
    },
    getListPrevious () {
      var _this = this
      if (LocalStorage.has('auth')) {
        getauth(_this.pathname_previous, {}).then(res => {
          _this.table_list = res.results
          _this.pathname_previous = res.previous
          _this.pathname_next = res.next
        }).catch(err => {
          _this.$q.notify({
            message: err.detail,
            icon: 'close',
            color: 'negative'
          })
        })
      } else {
      }
    },
    getListNext () {
      var _this = this
      if (LocalStorage.has('auth')) {
        getauth(_this.pathname_next, {}).then(res => {
          _this.table_list = res.results
          _this.pathname_previous = res.previous
          _this.pathname_next = res.next
        }).catch(err => {
          _this.$q.notify({
            message: err.detail,
            icon: 'close',
            color: 'negative'
          })
        })
      } else {
      }
    },
    refresh () {
      var _this = this
      _this.getList()
    },
    editData (e) {
      var _this = this
      _this.editMode = true
      _this.editid = e.id
      _this.editFormData = {
        supplier_name: e.supplier_name,
        supplier_city: e.supplier_city,
        supplier_address: e.supplier_address,
        supplier_contact: e.supplier_contact,
        supplier_manager: e.supplier_manager,
        supplier_level: e.supplier_level,
        creater: _this.login_name
      }
    },
    deleteDataSubmit () {
      var _this = this
      deleteauth(_this.pathname + _this.deleteid + '/').then(res => {
        _this.deleteDataCancel()
        _this.getList()
        _this.$q.notify({
          message: 'Success Edit Data',
          icon: 'check',
          color: 'green'
        })
      }).catch(err => {
        _this.$q.notify({
          message: err.detail,
          icon: 'close',
          color: 'negative'
        })
      })
    },
    deleteDataCancel () {
      var _this = this
      _this.deleteForm = false
      _this.deleteid = 0
    },
    downloadData () {
      var _this = this
      if (LocalStorage.has('auth')) {
        getfile(_this.pathname + 'file/?lang=' + LocalStorage.getItem('lang')).then(res => {
          var timeStamp = Date.now()
          var formattedString = date.formatDate(timeStamp, 'YYYYMMDDHHmmssSSS')
          const status = exportFile(
            _this.pathname + formattedString + '.csv',
            '\uFEFF' + res.data,
            'text/csv'
          )
          if (status !== true) {
            _this.$q.notify({
              message: 'Browser denied file download...',
              color: 'negative',
              icon: 'warning'
            })
          }
        })
      } else {
        _this.$q.notify({
          message: _this.$t('notice.loginerror'),
          color: 'negative',
          icon: 'warning'
        })
      }
    }
  },
  created () {
    var _this = this
    if (LocalStorage.has('openid')) {
      _this.openid = LocalStorage.getItem('openid')
    } else {
      _this.openid = ''
      LocalStorage.set('openid', '')
    }
    if (LocalStorage.has('login_name')) {
      _this.login_name = LocalStorage.getItem('login_name')
    } else {
      _this.login_name = ''
      LocalStorage.set('login_name', '')
    }
    if (LocalStorage.has('auth')) {
      _this.authin = '1'
      _this.getList()
    } else {
      _this.authin = '0'
    }
  },
  mounted () {
    var _this = this
    if (_this.$q.platform.is.electron) {
      _this.height = String(_this.$q.screen.height - 290) + 'px'
    } else {
      _this.height = _this.$q.screen.height - 290 + '' + 'px'
    }
  },
  updated () {
  },
  destroyed () {
  },
  components: {
    CommonTable,
    GoodsSearch
  }
}
</script>
