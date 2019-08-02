#include <queue>

/*
 * This file contans class that represents the actual data 
 * of one of the devices.
 */

class Data
{
  public:
    Data(int i, float T, float H);
    int get_index();
    float get_avr_T();
    float get_avr_H();
    void update(float T, float H);
  private:
    int index;
    std::queue<float> queueT;
    std::queue<float> queueH;
};

Data::Data(int i, float T, float H)
{
  index = i;
  for (int i = 0; i < 10; ++i) {
    queueT.push(T);
    queueH.push(H);
  }
}

int Data::get_index()
{
  return index;
}

float Data::get_avr_T()
{
  float avg_val = 0;
  std::queue<float> queueTemp = queueT;
  for (int i = 0; i < 10; ++i) {
    avg_val += queueTemp.front();
    queueTemp.pop();
  }
  return avg_val / 10;
}

float Data::get_avr_H()
{
  float avg_val = 0;
  std::queue<float> queueTemp = queueH;
  for (int i = 0; i < 10; ++i) {
    avg_val += queueTemp.front();
    queueTemp.pop();
  }
  return avg_val / 10;
}

void Data::update(float T, float H)
{
  queueT.pop();
  queueT.push(T);
  queueH.pop();
  queueH.push(H);
}
