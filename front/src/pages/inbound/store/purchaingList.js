function PurchaingListStore(goodsToPurchaseList, goodsWaitingList, goodsToSortedList, goodsInStockList) {
  const phases = {
    purchase: '待下单',
    waiting: '采购中',
    sort: '待分拣',
    stock: '已入库'
  };

  var goodsToPurchaseList = goodsToPurchaseList;

  var goodsWaitingList = goodsWaitingList;

  var goodsToSortedList = goodsToSortedList;


  var goodsInStockList = goodsInStockList;

  this.addToPurchase = function(goods) {
    goods.forEach(elemengt => {
      let find = false;
      console.log("add good ", elemengt.goods_supplier);
      goodsToPurchaseList.forEach(goodsGroup => {
        // 判断是否已有供应商
        if (goodsGroup.goods_supplier === elemengt.goods_supplier) {
          find = true;
          console.log("add good exit ", goodsGroup.goods_supplier);
          // 判断是不是已有的产品
          let existGoods = goodsGroup.items;
          let exist = false;
          existGoods.forEach((existGood) => {
            if (existGood.goods_code == elemengt.goods_code) {
              console.log("goods exist ", elemengt.goods_code);
              existGood.goods_stock_purchase += elemengt.goods_stock_purchase;
              exist = true;
              return;
            }
          })
          if (!exist) {
            console.log("goods ", elemengt.goods_code, " not exist yet");
            goodsGroup.items.push(elemengt);
          }
          // 把商品的库存信息累加
          goodsGroup.goods_stock_consume += elemengt.goods_stock_consume;
          goodsGroup.order_num += Math.round(Math.random() * 100); // TODO
          goodsGroup.goods_stock_purchase += elemengt.goods_stock_purchase;
          goodsGroup.goods_stock_reserved += elemengt.goods_stock_reserved;
          return;
        }
      });
      if (!find) {
        console.log("add good not exit ", elemengt);
        let date = new Date();
        let asn =
        "ANS-" +
        date.getFullYear() +
        date.getMonth() +
        date.getDay() +
        date.getHours() +
        date.getMinutes() +
        "-" +
        Math.round(Math.random() * 100);
        goodsToPurchaseList.push({
          asn_code: asn,
          asn_status: 0,
          goods_supplier: elemengt.goods_supplier,
          goods_stock_consume: elemengt.goods_stock_consume,
          order_num: elemengt.order_num,
          goods_stock_reserved: elemengt.goods_stock_reserved,
          goods_stock_purchase: elemengt.goods_stock_purchase,
          goods_price: elemengt.goods_stock_purchase * elemengt.goods_price,
          items: [elemengt],
          creater: "admin",
          create_time: "2022/05/30"
        });
      }
    })
  }

  this.moveToPrePhase = function(currentPhase, index) {
    // TODO

  }

  this.duplicateItem = function(currentPhase, index) {
    if (index < 0) {
      throw new Error("dumplcate item index must be none negetive");
    }
    let target = undefined;
    if (phases.purchase == currentPhase) {
      target = goodsToPurchaseList[index];
    } else if (phases.waiting == currentPhase) {
      target = goodsWaitingList[index];
    } else if (phases.sort == currentPhase) {
      target = goodsToSortedList[index];
    } else if (phases.stock == currentPhase){
      target = goodsInStockList[index];
    } else {
      throw new Error("moveToNextPhase Wrong phase :", currentPhase);
    }
    let cloneTarget = {... target};
    let goods = cloneTarget.items;
    this.addToPurchase(goods);
  }

  this.removeItemInPhase = function(currentPhase , index) {
    console.log("removeItemInPhase ", currentPhase, index);
    if (phases.purchase == currentPhase) {
      goodsToPurchaseList.splice(index, 1);
    } else if (phases.waiting == currentPhase) {
      goodsWaitingList.splice(index, 1);
    } else if (phases.sort == currentPhase) {
      goodsToSortedList.splice(index, 1);
    } else if (phases.stock == currentPhase){
      goodsInStockList.splice(index, 1);
    } else {
      throw new Error("moveToNextPhase Wrong phase :", currentPhase);
    }
  };

  this.moveToNextPhase = function (currentPhase, index) {
    console.log("move to next Phase 2 ", currentPhase, index);
    if (phases.purchase == currentPhase) {
      this.fromPurchaseToWaiting(index);
    } else if (phases.waiting == currentPhase) {
      this.fromWaitingToSort(index);
    } else if (phases.sort == currentPhase) {
      this.fromSortToStock(index);
    } else {
      throw new Error("moveToNextPhase Wrong phase :", currentPhase);
    }
  }

  this.fromPurchaseToWaiting = function(index) {
    let goodsGroup = goodsToPurchaseList.splice(index, 1)[0];
    goodsGroup.asn_status = 1;
    goodsWaitingList.push(goodsGroup)
  };

  this.fromWaitingToSort = function(index) {
    let goods = goodsWaitingList.splice(index, 1)[0];
    let date  = new Date();
    let receivedDate = date.getFullYear() + date.getMonth() + date.getDate();
    goods['receivedDate'] = receivedDate;
    goodsToSortedList.push(goods);
  };

  this.fromSortToStock = function(index) {
    let goods = goodsToSortedList.splice(index, 1)[0];
    goodsInStockList.push(goods);
  };

  this.getToPurchaseMap = function() {
    return goodsToPurchase;
  };

  this.getGoodsWaiting = function() {
    return Array.from(goodsWaiting);
  };

  this.getGoodsToSorted = function() {
    return Array.from(goodsToSorted);
  };

  this.getGoodsInStock = function() {
    return Array.from(goodsInStock);
  };

  this.getPhases = function() {
    return phases;
  }
}

export { PurchaingListStore };
