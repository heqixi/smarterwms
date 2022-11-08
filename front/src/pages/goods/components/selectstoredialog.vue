<template>
  <q-dialog ref="dialog" class="shadow-24">
    <q-card :style="{width: '700px', maxWidth:'700px'}">
      <q-bar
        :show="!loading"
        class="bg-light-blue-10 text-white rounded-borders"
        style="height: 50px">
        <div v-if="title">
          {{ title }}
        </div>
        <div v-else>{{ $t('newtip') }}</div>
        <q-space/>
        <q-btn dense flat icon="close" v-close-popup>
          <q-tooltip content-class="bg-amber text-black shadow-4">{{
            $t('index.close')
            }}
          </q-tooltip>
        </q-btn>
      </q-bar>
      <q-card :show="!loading" bordered v-for="(merchant, merchantIdx) in merchants" :key="merchantIdx">
        <q-card-section horizontal>
          <q-card-section>
            <div :style="{whiteSpace: 'normal', display: 'flex', justifyContent:'center',alignItems:'center'}">
              {{merchant.name}}
            </div>
          </q-card-section>
          <q-separator vertical/>
          <q-card-section>
            <div v-for="(storegroup, index) in merchant.storeGroups" :key="index">
              <div class="row justify-start">{{storegroup.area}}:</div>
              <div v-if="storegroup.storeList.length > 1">
                <q-radio v-for="(store, storeIdx) in storegroup.storeList" :key="storeIdx"
                         v-model="storegroup.selected" checked-icon="task_alt" unchecked-icon="panorama_fish_eye"
                         :val="store" :label="store.name"/>
              </div>
              <div v-else>
                <q-toggle v-model="storegroup.selected" :label="storegroup.storeList[0].name"></q-toggle>
              </div>
            </div>
          </q-card-section>
        </q-card-section>
      </q-card>
      <div :show="!loading" style="float: right; padding: 15px 15px 15px 0">
        <q-btn
          color="white"
          text-color="black"
          style="margin-right: 25px"
          @click="hide()"
        >{{ $t('cancel') }}
        </q-btn>
        <q-btn color="primary" @click="onStoreSelect()">{{ $t('submit') }}</q-btn>
      </div>
      <q-inner-loading :showing="loading">
      </q-inner-loading>
    </q-card>
  </q-dialog>
</template>

<script>
import { getauth } from 'boot/axios_request'

export default {
  name: 'SelectStore',
  data () {
    return {
      merchants: [],
      loading: false
    }
  },
  methods: {
    show () {
      this.$refs.dialog.show()
    },
    hide () {
      this.$refs.dialog.hide()
    },
    onStoreSelect () {
      const selectedStore = []
      console.log('onStoreSelect ', this.merchants)
      this.merchants.forEach(merchant => {
        merchant.storeGroups.forEach(group => {
          if (group.selected) {
            if (group.storeList.length <= 1) {
              selectedStore.push(group.storeList[0])
            } else {
              selectedStore.push(group.selected)
            }
          }
        })
      })
      console.log('onStoreSelect ', this.selectedStore)
      this.$emit('ok', selectedStore)
      this.hide()
    },
    getAllStore () {
      var _this = this
      _this.loading = true
      getauth('store/all?type=all&profit_settings=true', {}).then(storeList => {
        console.log('get store list ', storeList)
        storeList.forEach(store => {
          if (!store.merchant) {
            _this.merchants.push(store)
          }
        })
        storeList.forEach(store => {
          if (store.merchant !== undefined && store.merchant !== null) {
            const merchant = _this.merchants.find(merchant => {
              return merchant.id === store.merchant
            })
            if (!merchant.storeGroups) {
              _this.$set(merchant, 'storeGroups', [])
            }
            let existGroup = merchant.storeGroups.find(group => {
              return group.area === store.area
            })
            if (!existGroup) {
              existGroup = {
                area: store.area,
                storeList: [],
                selected: undefined
              }
              merchant.storeGroups.push(existGroup)
            }
            existGroup.storeList.push(store)
          }
        })
        _this.loading = false
      })
    }
  },
  created () {
    this.getAllStore()
    // if (this.data) {
    //   console.log('merchants ', this.data)
    //   this.merchants = this.data
    // }
  },
  emits: [
    // REQUIRED
    'ok',
    'cancel',
    'update'
  ],
  props: ['data', 'title']
}
</script>

<style scoped>

</style>
