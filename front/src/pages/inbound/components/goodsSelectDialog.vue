<template>
  <div>
    <q-dialog ref="dialog">
      <q-card>
        <goods-search-dialog
          :columns="columns"
          :topButtons="topButtons"
          :goods="goods"
          rowsPerPage="200"
          hideSearch="true"
          multiple-select="true"
        />
      </q-card>
    </q-dialog>
  </div>
</template>
<script>
import GoodsSearchDialog from 'src/components/Share/goodsSearchTable'

export default {
  name: 'GoodsSelected',
  components: { GoodsSearchDialog },
  data () {
    const _this = this
    return {
      topButtons: [
        {
          name: 'confirm',
          label: `${this.$t('submit')}`,
          tip: `${this.$t('submit')}`,
          click: selectedList => {
            console.log('selectedList, ', selectedList.length)
            _this.$emit('ok', selectedList)
            _this.hide()
          }
        },
        {
          name: 'cancel',
          label: '取消',
          tip: '下次再选',
          click: selectedList => {
            console.log('cancel selectedList, ', selectedList.length)
            _this.$refs.dialog.hide()
          }
        }
      ],
      columns: [
        {
          name: 'goods_image',
          required: true,
          label: '图片',
          align: 'center',
          type: 'image',
          field: 'goods_image'
        },
        {
          name: 'goods_code',
          required: true,
          label: this.$t('goods.view_goodslist.goods_code'),
          align: 'center',
          type: 'text',
          field: 'goods_code',
          style: {
            whiteSpace: 'normal'
          }
        }
      ]
    }
  },
  props: {
    goods: Array
  },
  emits: [
    // REQUIRED
    'ok',
    'cancel',
    'update'
  ],
  methods: {
    submit (data) {
      this.$emit('ok', data)
      this.hide()
    },
    show () {
      this.$refs.dialog.show()
    },
    hide () {
      this.$refs.dialog.hide()
    }
  }
}
</script>
