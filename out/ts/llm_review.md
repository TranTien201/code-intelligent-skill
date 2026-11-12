# Cần review (chỉ snippet liên quan)

## Xung đột: `Clamp`  (Clamp <- TonerSave_ApplyDensity)
**A_latest:**
```c
int Clamp(int v, int lo, int hi)
{
    if (v < lo) return lo;
    if (v > hi) return hi;
    return v;
}
```
**B_latest:**
```c
int Clamp(int v, int hi)
{
    if (v < 0) return 0;
    if (v > hi) return hi;
    return v;
}
```
B đang dùng ở: []

## Drift: `TonerSave_ApplyDensity` đã đổi sau commit feature -> dùng bản A_latest
```c
int TonerSave_ApplyDensity(int density)
{
    int level = TonerSave_GetLevel();
    level = Clamp(level, TONER_SAVE_OFF, TONER_SAVE_HIGH); /* fix #1234: NV value hong */
    if (!is_valid(level))
        return density;
    return Density_Scale(density, k_percent[level]);
}
```

## Phụ thuộc chiều vào: `EcoReport_Print` dùng `TONER_SAVE_OFF`
```c
void EcoReport_Print(void)
{
    if (TonerSave_GetLevel() != TONER_SAVE_OFF)
        Log_Info("Eco: toner save ON");
}
```

## Phụ thuộc chiều vào: `EcoReport_Print` dùng `TonerSave_GetLevel`
```c
void EcoReport_Print(void)
{
    if (TonerSave_GetLevel() != TONER_SAVE_OFF)
        Log_Info("Eco: toner save ON");
}
```
