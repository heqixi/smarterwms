<style>
.input-padding {
  padding: 0 20px 0 0;
}
</style>
<template>
  <q-dialog ref="dialog" no-backdrop-dismiss>
    <q-card class="q-pa-md" style="width: 700px; max-width: 80vw;">
      <q-banner rounded dense class="bg-white" v-if="modifyType === 1">
        <template v-slot:avatar>
          {{$t('order.view_details.reissue')}}
        </template>
      </q-banner>
      <q-banner rounded dense class="bg-white" v-if="modifyType === 2">
        <template v-slot:avatar>
          {{$t('order.view_details.replace')}}
        </template>
      </q-banner>
      <q-separator/>
      <q-card-section class="row" v-if="modifyType === 2">
        <div class="col-2">
          {{$t('order.view_details.original_product')}}
        </div>
        <q-img :src="item.image_url"
               :ratio="1"
               style="max-height: 100px; max-width: 100px"
               basic
               spinner-color="white"
               class="col-4 rounded-borders"
        >
          <template v-slot:error>
            <q-icon name="error"></q-icon>
          </template>
          <div class="no-padding absolute-bottom text-center text-italic text-body2">
            X {{item.model_quantity_purchased}}
          </div>
        </q-img>
        <div class="col-6 center-padding overflow-hidden">
          <div>{{$t('order.view_details.item_sku')}}: {{item.item_sku}}</div>
          <div>{{$t('order.view_details.model_name')}}: {{item.model_name}}</div>
          <div>{{$t('order.view_details.model_sku')}}: {{item.model_sku}}</div>
        </div>
      </q-card-section>
      <q-separator/>
      <q-card-section class="row">
        <div class="col-10 self-center no-outline">
          {{$t('order.view_details.selected_products')}}
        </div>
        <div class="col-2">
          <q-btn align="center" class="float-right" dense icon="add"
                 @click="newModel"></q-btn>
        </div>
      </q-card-section>
      <q-card-section class="row q-pa-md">
        <div v-for="(model, index) in modelList" :key="index" class="row full-width">
          <q-input class="col-4 input-padding" dense clearable v-model="model.globalSku" readonly
                   :label="$t('store.view_productlist.item_sku')" @blur="inspectionModel(model)"/>
          <q-input class="col-4 input-padding" dense clearable v-model="model.quantity"
                   :label="$t('store.view_productlist.quantity')" @blur="inspectionQuantity(model)"/>
          <div class="col-4 self-center vertical-top">
            <q-btn v-if="model.imageUrl" align="center" class="float-left" :label="$t('check')" dense @click="checkModelImage(model)"></q-btn>
            <q-btn align="center" class="float-right" dense icon="delete" @click="removeModel(index)"></q-btn>
          </div>
        </div>
      </q-card-section>
      <q-card-actions align="right">
        <q-btn :label="$t('index.cancel')" @click="cancel"></q-btn>
        <q-btn :label="$t('index.submit')" color="primary" text-color="white" @click="submit"></q-btn>
      </q-card-actions>
    </q-card>
  </q-dialog>
</template>
<script>
import ZoomImage from 'pages/order/components/zoomimage'
import GoodsSearch from 'pages/order/components/goodssearch'
export default {
  name: 'OrderModify',
  data () {
    return {
      modelList: []
    }
  },
  props: {
    item: Object,
    parent: {
      type: Object,
      require: true
    },
    modifyType: {
      type: Number,
      require: true
    }
  },
  methods: {
    submit () {
      const _this = this;
      const result = {
        modifyType: _this.modifyType,
        modelList: _this.modelList.filter((model) => model.quantity > 0)
      };
      if (result.modelList.length > 0) {
        if (_this.modifyType === 2) {
          if (_this.item.model_id !== '0') {
            result.id = _this.item.id
            result.replacedId = _this.item.model_id
            result.replacedSku = _this.item.model_sku
          } else {
            result.id = _this.item.id
            result.modifyType = 3
            result.replacedId = _this.item.item_id
            result.replacedSku = _this.item.item_sku
          }
        }
        _this.$emit('ok', result);
      } else {
        _this.$q.notify({
          message: 'The replacement quantity must be greater than 0',
          icon: 'close',
          color: 'negative'
        })
      }
      this.hide()
    },
    cancel () {
      this.hide()
    },
    checkModelImage (model) {
      const _this = this
      _this.$q.dialog({
        component: ZoomImage,
        parent: _this,
        img_url: model.imageUrl
      })
    },
    newModel () {
      const _this = this;
      _this.$q.dialog({
        component: GoodsSearch
      }).onOk(goodsList => {
        for (const i in goodsList) {
          const goods = goodsList[i]
          _this.modelList.push({
            goodsId: goods.id,
            globalSku: goods.goods_code,
            imageUrl: goods.goods_image,
            quantity: 0
          })
        }
      })
    },
    inspectionModel () {
      // TODO 检查是否存在该SKU
    },
    inspectionQuantity (model) {
      if (this.modifyType === 2) {
        let total = 0
        // eslint-disable-next-line no-return-assign
        this.modelList.forEach(model => total += parseInt(model.quantity))
        if (this.item.model_quantity_purchased < total) {
          this.$q.dialog({
            message: 'The replaced quantity cannot be greater than the original quantity',
            icon: 'close',
            color: 'negative'
          })
          model.quantity = 0
        }
      }
    },
    removeModel (index) {
      if (index >= 0) {
        this.modelList.splice(index, 1);
      }
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
