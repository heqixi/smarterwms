<template>
  <div style="width:1200px;max-width:1500px">
      <q-dialog :ref="refName">
        <div style="width:1200px;max-width:1500px" @focusin="stopPropagation">
          <q-card style="width:1200px;max-width:1500px" >
            <CommonTable
              ref="purchaseTable"
              :table_list="table_list"
              :rowKey="rowKey"
              :columns="columns"
              :numRows="numRows"
              :loading="loading"
              :topButtons="topButtons"
              :filterFn="filteredRows"
              :getNextPage="getListNext"
              :searchFn="getSearchList"
              @refresh="refresh"
            />
          </q-card>
        </div>
      </q-dialog>
    <q-dialog v-model="newDataDialog">
      <NewForm
        :items="newFormItems"
        :newFormData="newFormData"
        @newDataSummit="onNewDataSummit"
        @newDataCancel="onNewDataCancel"
      />
    </q-dialog>
  </div>
</template>
<router-view/>

<script>
import { getauth, postauth } from 'boot/axios_request'
import { LocalStorage } from 'quasar'
import CommonTable from 'src/components/Share/commontable'
import NewForm from 'components/Share/newForm'
import NewFormDialog from 'components/Share/newFormDialog'

export default {
  name: 'PurchaseSelectedDialog',
  data () {
    var _this = this
    return {
      openid: '',
      login_name: '',
      authin: '0',
      rowKey: 'id',
      numRows: 0,
      newDataDialog: false,
      newFormItems: [],
      onNewDataSummit: undefined,
      onNewDataCancel: undefined,
      newFormData: {},
      pathname: 'supplier/purchase/',
      pathname_previous: '',
      pathname_next: '',
      separator: 'cell',
      loading: false,
      height: '',
      table_list: [],
      suppliers: [],
      purchaseFormData: {
        tag: '',
        url: '',
        supplier: '',
        price: '',
        image_url: ''
      },
      supplierForm: {
        supplier_name: '',
        supplier_city: '',
        supplier_address: '',
        supplier_contact: '',
        supplier_manager: '',
        supplier_level: 1
      },
      topButtons: [
        {
          name: 'new',
          label: '确定',
          tip: '选择当前购买链接',
          click: (purchaseList) => {
            console.log('select purchase ', purchaseList)
            if (purchaseList.length <= 0) {
              this.$q.notify({
                message: '请选择一个采购方案',
                icon: 'check',
                color: 'green'
              })
              return
            }
            _this.$emit('ok', purchaseList[0])
            _this.hide()
          }
        },
        {
          name: 'confirm',
          label: '新增购买链接',
          tip: '供应商新增购买链接',
          click: () => {
            _this.newPurchasePlan()
          }
        }
      ],
      columns: [
        {
          name: 'image_url',
          label: '图片',
          field: 'image_url',
          type: 'image',
          style: { width: '80px', maxWidth: '80px', textAlign: 'center', fontSize: '6px' }
        },
        {
          name: 'supplier',
          label: '供应商',
          field: 'supplier',
          type: 'text',
          style: { width: '80px', maxWidth: '80px', whiteSpace: 'normal', textAlign: 'center', fontSize: '6px' },
          fieldMap: supplier => {
            if (supplier) {
              return supplier.supplier_name
            }
            return '--'
          }
        },
        {
          name: 'tag',
          label: '标签',
          field: 'tag',
          type: 'text',
          style: { width: '80px', maxWidth: '80px', whiteSpace: 'normal',textAlign: 'center', fontSize: '6px' }
        },
        {
          name: 'price',
          label: '价格',
          field: 'price',
          type: 'number',
          style: { width: '50px' }
        },
        {
          name: 'url',
          label: '链接',
          type: 'url',
          field: 'url',
          style: { width: '50px' }
        },
        {
          name: 'action',
          label: this.$t('action'),
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
              name: 'set_default',
              label: '设为默认',
              tip: '设置为默认采购链接',
              click: (purchase) => {
                console.log('set as default purchase ', purchase)
                _this.$emit('ok', { purchase: purchase, action: 'set_default' })
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
      deleteid: 0
    }
  },
  methods: {
    stopPropagation (evt) {
      evt.stopPropagation()
    },
    addSelectedPurchase (purchase) {
      this.$refs.purchaseTable.addSelected([purchase.id])
    },
    async newPurchasePlan () {
      console.log('new purchase plan ')
      var _this = this
      await _this.getAllSupplier()
      _this.purchaseFormData.tag = ''
      _this.purchaseFormData.url = ''
      _this.purchaseFormData.supplier = undefined
      _this.purchaseFormData.price = ''
      _this.purchaseFormData.image_url = ''
      const purchaseFormItems = [
        {
          name: 'supplier',
          label: '选择或新增供应商',
          type: 'select',
          field: 'supplier',
          options: _this.suppliers,
          optionLabel: supplier => {
            return supplier.supplier_name
          },
          newValue: () => {
            _this.newSupplier()
              .then(supplier => {
                _this.purchaseFormData.supplier = supplier
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
          id: undefined,
          image_url: formData.image_url,
          partial: true
        }
        postauth('supplier/purchase/', planFormData)
          .then(purchasePlanSave => {
            console.log('new Purchase Plan save,', purchasePlanSave)
            this.$q.notify({
              message: '采购方案保存成功',
              icon: 'check',
              color: 'green'
            })
            purchasePlanSave.supplier = formData.supplier
            _this.purchases.unshift(purchasePlanSave)
            _this.addSelectedPurchase(purchasePlanSave)
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
        getauth(_this.pathname + '?supplier=true', {}).then(purchases => {
          console.log('get all purchases', purchases)
          _this.table_list = purchases
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
    filteredRows (purchase, searchTerm) {
      const tagMatch = purchase.tag.indexOf(searchTerm) > -1
      let nameMatch = false
      if (purchase.supplier && purchase.supplier.supplier_name) {
        nameMatch = purchase.supplier.supplier_name.indexOf(searchTerm) > -1
      }
      const urlMatch = purchase.url === searchTerm
      return tagMatch || nameMatch || urlMatch
    },
    getSearchList () {
      console.log('all data load')
    },
    getListPrevious () {
      console.log('all data load')
    },
    getListNext () {
      console.log('all data load at first time')
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
    show () {
      this.$refs[this.refName].show()
    },
    hide () {
      this.$refs[this.refName].hide()
    },
    async getAllSupplier () {
      var _this = this
      if (_this.suppliers.length > 0) {
        return _this.suppliers
      }
      const res = await getauth('supplier/', {})
      console.log('get all supplier ', res)
      _this.suppliers = res.results
    }
  },
  created () {
    var _this = this
    if (this.additionalTopButtons) {
      this.additionalTopButtons.forEach(button => {
        _this.topButtons.push(button)
      })
    }
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
      if (!_this.purchases) {
        _this.getList()
      } else {
        console.log('init with purchases ', _this.purchases)
        _this.table_list = _this.purchases
      }
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
  props: ['refName', 'purchases', 'additionalTopButtons'],
  components: {
    CommonTable,
    NewForm
  }
}
</script>
