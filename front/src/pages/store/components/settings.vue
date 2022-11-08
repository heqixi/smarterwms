<style>
.q-card-padding {
  padding: 5px;
}
.q-card-section-margin {
  margin: 5px 0
}
.q-card-section-border {
  border: 1px solid rgba(0,0,0, 0.1);
  border-radius: 10px;
}
.q-card-section-input-padding {
  padding: 0 5px;
}
</style>
<template>
  <q-dialog ref="dialog">
    <q-card class="q-dialog-plugin q-card-section-margin q-card-padding">
      <q-banner rounded dense class="bg-white">
        <template v-slot:avatar>
          <q-icon name="settings"></q-icon>
          {{$t('settings')}}
        </template>
      </q-banner>
      <q-card-section class="bg-grey-2 q-card-section-border">
        <q-field borderless dense>
          <template v-slot:control class="q-pa-md">
            <div class="row full-width">
              <div class="col self-center no-outline">
                {{ $t('store.view_productlist.wholesale') }}
              </div>
              <div class="col">
                <q-btn align="center" class="float-right" dense icon="add"
                       @click="newWholesale"></q-btn>
              </div>
            </div>
            <div v-for="(setting, index) in wholesale" :key="index" class="row full-width">
              <q-input class="col-3 q-card-section-input-padding" dense clearable v-model="setting.min"
                       :label="$t('store.view_productlist.min_quantity')" @blur="checkWholesale"/>
              <q-input class="col-3 q-card-section-input-padding" dense clearable v-model="setting.max"
                       :label="$t('store.view_productlist.max_quantity')" @blur="checkWholesale"/>
              <q-input class="col-3 q-card-section-input-padding" dense clearable v-model="setting.price"
                       :label="$t('store.view_productlist.price')" @blur="checkWholesale"/>
              <div class="col-3 self-center">
                <q-btn align="center" class="float-right" dense icon="delete" @click="removeWholesale(index)"></q-btn>
              </div>
            </div>
          </template>
        </q-field>
      </q-card-section>
      <q-card-section class="bg-grey-2 q-card-section-margin q-card-section-border">
        <q-field borderless dense>
          <template v-slot:control class="q-pa-md">
            <div class="self-center no-outline">
              <q-icon name="local_offer" color="grey-5"/>
              {{ $t('store.view_productlist.discount') }}
            </div>
            <div v-for="(price, index) in price_list" :key="index" class="row full-width">
              <q-input class="col-6 q-card-section-input-padding" dense clearable v-model="price.current"
                       :label="$t('store.view_productlist.price')" disable/>
              <q-input class="col-6 q-card-section-input-padding" dense clearable v-model="price.discount"
                       :label="$t('store.view_productlist.discount_price')" @blur="checkPrice"/>
            </div>
          </template>
        </q-field>
      </q-card-section>
      <q-card-actions align="right">
        <q-btn :label="$t('cancel')" @click="hide" />
        <q-btn color="primary" :label="$t('submit')" @click="submit" />
      </q-card-actions>
    </q-card>
  </q-dialog>
</template>

<script>

export default {
  name: 'Settings',
  data () {
    return {
      wholesale: [],
      price_list: [],
      item_id: '',
      pathname: 'store/product/setting'
    }
  },
  props: {
    item: null,
    shop_id: null
  },
  methods: {
    show () {
      this.$refs.dialog.show()
    },
    // following method is REQUIRED
    // (don't change its name --> "hide")
    hide () {
      this.$refs.dialog.hide()
    },
    checkPrice () {
    },
    checkWholesale () {
      const _this = this;
      console.log(_this.wholesale)
    },
    newWholesale () {
      const _this = this;
      _this.wholesale.push({
        min: '',
        max: '',
        price: ''
      })
    },
    removeWholesale (index) {
      if (index >= 0) {
        this.wholesale.splice(index, 1);
      }
    },
    submit () {
      // TODO Request Setting Product
    }
  }
}
</script>
