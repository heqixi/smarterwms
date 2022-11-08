<template>
  <q-page class="flex flex-top">
    <template>
      <div class="q-pa-md">
        <div class="q-gutter-y-md" style="max-width: 100%">
          <q-tabs v-model="detaillink">
            <transition appear enter-active-class="animated zoomIn">
              <q-route-tab
                name="storemanagement"
                :label="$t('store.storemanagement')"
                icon="img:statics/store/store.svg"
                :to="{ name: 'storemanagement' }"
                exact
              />
            </transition>
            <transition appear enter-active-class="animated zoomIn">
              <q-route-tab
                  name="globalproductlist"
                  :label="$t('store.globalproductlist')"
                  icon="public"
                  :to="{ name: 'globalproductlist' }"
                  exact
              />
            </transition>
            <transition appear enter-active-class="animated zoomIn">
              <q-route-tab
                name="productlist"
                :label="$t('store.productlist')"
                icon="img:statics/store/product.svg"
                :to="{ name: 'productlist' }"
                exact
              />
            </transition>
            <transition appear enter-active-class="animated zoomIn">
              <q-route-tab
                  name="productpackage"
                  :label="$t('store.productpackage')"
                  icon="view_list"
                  :to="{ name: 'productpackage' }"
                  exact
              />
            </transition>
          </q-tabs>
        </div>
      </div>
    </template>
    <div class="main-table">
      <router-view />
    </div>
  </q-page>
</template>

<script>

export default {
  name: 'Pagestore',
  data () {
    return {
      detaillink: 'storemanagement'
    }
  },
  methods: {}
}
</script>
