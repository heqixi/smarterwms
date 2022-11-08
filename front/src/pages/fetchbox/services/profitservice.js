import { LocalStorage } from 'quasar';

class GradientFee {
  constructor (intervalWeight, fee, fixed, minWeight, maxWeight) {
    this.minWeight = minWeight * 1000;
    this.maxWeight = maxWeight ? maxWeight * 1000 : null;
    this.intervalWeight = intervalWeight ? intervalWeight * 1000 : null;
    this.fee = fee;
    this.fixed = fixed;
  }
}

class Logistics {
  constructor (gradientFees) {
    this.gradientFees = gradientFees;
  }

  getLogisticsFee (weight) {
    let logisticsFee = 0;
    let tempWeight = weight;
    for (let i = 0; i < this.gradientFees.length; i++) {
      const gradientFee = this.gradientFees[i];
      if (tempWeight > 0) {
        let _weight = tempWeight;
        if (gradientFee.maxWeight) {
          _weight = tempWeight < gradientFee.maxWeight ? tempWeight : gradientFee.maxWeight - gradientFee.minWeight;
        }
        if (gradientFee.fixed) {
          logisticsFee += gradientFee.fee;
        } else {
          logisticsFee += Math.ceil(_weight / gradientFee.intervalWeight) * gradientFee.fee;
        }
        tempWeight -= _weight;
      } else {
        break;
      }
    }
    return logisticsFee;
  }
}

class ProfitService {
  // 佣金费
  getCommissionFee (areaInfo, price, number) {
    return number * price * areaInfo.commission_rate;
  }

  // 活动费
  getActivityFee (areaInfo, price, number) {
    return number * price * areaInfo.activity_rate;
  }

  // 交易费
  getTransactionFee (areaInfo, price, number) {
    return (number * price + areaInfo.buyer_shipping) * areaInfo.transaction_rate;
  }

  // 收入
  getIncome (areaInfo, price, number, weight) {
    const commissionFee = this.getCommissionFee(areaInfo, price, number);
    const activityFee = this.getActivityFee(areaInfo, price, number);
    const transactionFee = this.getTransactionFee(areaInfo, price, number);
    const crossLogisticsFee = this.getLogisticsFee(areaInfo, weight, number);
    return this.getIncomeByFee(number * price, activityFee, commissionFee, transactionFee, crossLogisticsFee);
  }

  // 收入
  getIncomeByFee (price, activityFee, commissionFee, transactionFee, crossLogisticsFee) {
    return price - activityFee - commissionFee - transactionFee - crossLogisticsFee;
  }

  // 提现费
  getWithdrawalFee (areaInfo, income) {
    return income > 0 ? income * areaInfo.withdrawal_rate : 0;
  }

  // 汇损
  getExchangeLossFee (areaInfo, income) {
    return income > 0 ? income * areaInfo.exchange_loss_rate : 0;
  }

  // 利润率
  getProfitMargin (areaInfo, netProfit, price, number) {
    return (netProfit * areaInfo.exchange_rate) / (price * number);
  }

  // 净利润
  getNetProfit (areaInfo, price, number, weight, cost, logisticsCosts) {
    const income = this.getIncome(areaInfo, price, number, weight);
    const withdrawalFee = this.getWithdrawalFee(areaInfo, income);
    const exchangeLossFee = this.getExchangeLossFee(areaInfo, income);
    return (income - withdrawalFee - exchangeLossFee -
      (cost * number + logisticsCosts + areaInfo.other_fee) * areaInfo.exchange_rate) / areaInfo.exchange_rate;
  }

  /*
  (((x * areaInfo.exchange_rate + (cost * number + logisticsCosts + areaInfo.other_fee) * areaInfo.exchange_rate)
  /(1-areaInfo.withdrawal_rate-areaInfo.exchange_loss_rate))  + areaInfo.buyer_shipping * areaInfo.transaction_rate + crossLogisticsFee)
  /(number*(1 - areaInfo.activity_rate - areaInfo.commission_rate - areaInfo.transaction_rate))
   = price
  * */
  getPriceByNetProfit (areaInfo, netProfit, number, cost, logisticsCosts, weight) {
    const a = netProfit * areaInfo.exchange_rate + (cost * number + logisticsCosts + areaInfo.other_fee) * areaInfo.exchange_rate;
    const b = 1 - areaInfo.withdrawal_rate - areaInfo.exchange_loss_rate;
    const c = areaInfo.buyer_shipping * areaInfo.transaction_rate + this.getLogisticsFee(areaInfo, weight, number);
    const d = number * (1 - areaInfo.activity_rate - areaInfo.commission_rate - areaInfo.transaction_rate);
    return ((a / b) + c) / d;
  }

  getLogisticsFee (areaInfo, weight, number) {
    const weightSum = Math.ceil(number * weight * 1000);
    const gradientFees = [];
    areaInfo.logistics_calc_list.forEach(calc => {
      gradientFees.push(
        new GradientFee(calc.interval, calc.logistics_fee, calc.calc_type === 1, calc.min_weight, calc.max_weight)
      );
    });
    const logistics = new Logistics(gradientFees);
    return logistics.getLogisticsFee(weightSum);
  }
}

const profitService = new ProfitService();
export default profitService;
