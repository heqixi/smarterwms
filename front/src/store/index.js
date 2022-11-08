import Vue from 'vue'
import Vuex from 'vuex'

import fabchange from './fabchange'
import bardata from './bardata'
import scanedsolve from './scanedsolve'
import inbound from './inbound'
import stock from './stock'
import VueClipboard from 'vue-clipboard2'

Vue.use(Vuex)
Vue.use(VueClipboard)

/*
 * If not building with SSR mode, you can
 * directly export the Store instantiation;
 *
 * The function below can be async too; either use
 * async/await or return a Promise which resolves
 * with the Store instance.
 */

export default function (/* { ssrContext } */) {
  const Store = new Vuex.Store({
    modules: {
      fabchange,
      bardata,
      scanedsolve,
      inbound,
      stock
    },

    // enable strict mode (adds overhead!)
    // for dev mode and --debug builds only
    strict: process.env.DEBUGGING
  })

  return Store
}
