<template>
  <q-card class="q-mt-md">
    <q-banner inline-actions class="text-white bg-blue-5">基本信息</q-banner>
    <q-card-section>
      <div class="row justify-between">
        <div class="col-10">
          <q-input
            dense
            square
            autofocus
            v-model="productBaseInfo.name"
            :rules="[val => (val && val.length > 0) || error1]"
            @blur="saveName()">
            <template v-slot:before class="q-mb-sm">
              <span v-if="baseInfo.name.require" :style="{color:'red', fontSize:'8px'}"> * </span>
              <div class="text-body2">
                {{baseInfo.name.label}}
              </div>
            </template>
          </q-input>
        </div>
      </div>

      <div class="row justify-start">
        <div class="col-4">
          <q-input
            dense
            v-model="productBaseInfo.sku"
            :rules="[val => (val && val.length > 0) || error1]"
            @blur="saveSku()">
            <template v-slot:before class="q-mb-sm">
              <span v-if="baseInfo.sku.require" :style="{color:'red', fontSize:'8px'}"> * </span>
              <div class="text-body2">
                {{baseInfo.sku.label}}
              </div>
            </template>
          </q-input>
        </div>
        <div class="col-2 q-ml-md">
          <q-btn @click="autoGenerateSku">
            自动生成
          </q-btn>
        </div>
        <div class="col-2 q-ml-lg">
          <q-select
            dense
            square
            v-model="productBaseInfo.second_hand"
            :options="baseInfo.second_hand.options"
            :option-label="secondHand => {return secondHand ? '二手' : '全新'}"
            transition-show="scale"
            transition-hide="scale"
            :rules="[val => (val && val.length > 0) || error1]"
            @blur="saveStatus()">
            <template v-slot:before class="q-mb-sm">
              <span v-if="baseInfo.second_hand.require" :style="{color:'red', fontSize:'8px'}"> * </span>
              <div class="text-body2">
                {{baseInfo.second_hand.label}}
              </div>
            </template>
          </q-select>
        </div>
      </div>

      <div class="row q-mb-sm">
        <span v-if="baseInfo.desc.require" :style="{color:'red', fontSize:'8px'}"> * </span>
        <div class="text-body2">
          {{baseInfo.desc.label}}
        </div>
      </div>

      <div class="row justify-between">
        <div class="col-12">
          <q-editor
            v-model="productBaseInfo.desc"
            :definitions="{
              save: {
              tip: 'Save your work',
              icon: 'save',
              label: 'Save',
              handler: saveWork
            },
            upload: {
              tip: 'Upload to cloud',
              icon: 'cloud_uploac',
              label: 'Upload',
              handler: uploadIt
            },
            deleteKeyWords: {
                tip: '删除无用关键词',
                icon: 'clear',
                label: '删除关键词',
                handler: deleteKeyWorks
            },
            }"
            :toolbar="[ ['upload', 'save', 'deleteKeyWords']]">
          </q-editor>
        </div>
      </div>
    </q-card-section>
  </q-card>
</template>

<script>

import { uuidGenerator } from 'src/store/inbound/helper'
import {
  getauth,
} from 'boot/axios_request'

export default {
  name: 'GoodsBaseInfo',
  data () {
    return {
      getKeyWordsFilterTasks: undefined,
      keyWordsFilter: undefined,
      baseInfo: {
        name: {
          value: '',
          require: true,
          label: '商品名称'
        },
        sku: {
          value: '',
          require: true,
          label: '商品编码'
        },
        second_hand: {
          value: false,
          options: [true, false],
          require: true,
          label: '商品状况'
        },
        desc: {
          value: '',
          require: true,
          label: '商品描述'
        }
      },
      error1: this.$t('goods.view_goodslist.error1')
    }
  },
  methods: {
    autoGenerateSku () {
      if (!this.category || !this.category.original_category_name) {
        this.$q.notify({
          message: '请先完善类别信息',
          icon: 'close',
          color: 'negative'
        })
        return
      }
      console.log('auto generate sku for categories ', this.category)
      const categoryName = this.category.original_category_name.replaceAll(' ', '')
      const date = new Date()
      this.productBaseInfo.sku = categoryName + '_' + date.getFullYear() + (date.getMonth() + 1) + date.getDate() + '_' + uuidGenerator(4, 32)
      this.saveSku()
      console.log('auto generate sku for category ', categoryName)
    },
    uploadIt () {
      console.log('upload it')
    },
    saveWork () {
      console.log('save work')
    },
    deleteKeyWorks () {
      console.log('delete keywords ', this.productBaseInfo.desc)
      const desc = this.productBaseInfo.desc
      if (!desc || desc <= 0) {
        this.$q.notify({
          message: '产品描述为空',
          icon: 'check',
          color: 'green'
        })
        return
      }
      const splitLines = desc
        .replaceAll('<div>', '<br>')
        .replaceAll('</div>', '')
        .replaceAll('</br>', '<br>')
        .split('<br>')
      var _this = this
      if (!splitLines || splitLines.length === 0) {
        this.$q.notify({
          message: '产品描述为空',
          icon: 'check',
          color: 'green'
        })
        return
      }
      if (!this.keyWordsFilter || this.keyWordsFilter.length <= 0) {
        this.$q.notify({
          message: '暂无关键词配置',
          icon: 'check',
          color: 'green'
        })
        return
      }
      const deleteLines = []
      const afterFilter = splitLines.filter(line => { return line.length > 0 }).filter(line => {
        let match = false
        for (let i = 0; i < _this.keyWordsFilter.length; i++) {
          if (line.startsWith(_this.keyWordsFilter[i], 0)) {
            match = true
            deleteLines.push(line)
            break
          }
        }
        return !match
      }).join('<br>')
      this.productBaseInfo.desc = afterFilter
      console.log('after filter ', deleteLines)
    },
    saveName () {
      if (this.name !== this.baseInfo.name.value) {
        this.save(this.baseInfo.name.value, 'name')
      }
    },
    saveStatus () {
      if (this.second_hand !== this.baseInfo.second_hand.value) {
        this.save(this.baseInfo.second_hand.value, 'status')
      }
    },
    save (value, field) {
      this.$emit('onChange', value, field)
    },
    getKeyWordFilter () {
      var _this = this
      this.getKeyWordsFilterTasks = setTimeout(() => {
        console.log('start get key words filter')
        getauth('product/keyword_filter?shop_type=shopee', {}).then(keyWords => {
          _this.keyWordsFilter = keyWords
          _this.getKeyWordsFilterTasks = undefined
        })
      }, 200)
    },
    cancelGetKeyWordsTask () {
      if (this.getKeyWordsFilterTasks) {
        console.log('cancel get key words filter, ', this.getKeyWordsFilterTasks)
        clearTimeout(this.getKeyWordsFilterTasks)
      }
    }
  },
  watch: {
    productBaseInfo (old, newInfo) {
      console.log('product base info changed ', newInfo)
      this.baseInfo.name.value = newInfo.name || ''
      this.baseInfo.sku.value = newInfo.sku || ''
      this.baseInfo.second_hand.value = false
      this.baseInfo.desc.value = newInfo.desc
    }
  },
  created () {
    console.log('create, base info ', this.productBaseInfo)
    this.baseInfo.name.value = this.productBaseInfo.name || ''
    this.baseInfo.sku.value = this.productBaseInfo.sku || ''
    this.baseInfo.second_hand.value = false
    this.baseInfo.desc.value = this.productBaseInfo.desc
  },
  mounted () {
    this.getKeyWordFilter()
  },
  beforeDestroy () {
    this.cancelGetKeyWordsTask()
  },
  props: ['name', 'sku', 'second_hand', 'desc', 'category', 'productBaseInfo']
}
</script>
