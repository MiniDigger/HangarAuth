package io.papermc.paperauth.db;

public class HangarAuthDao<T> {

    private final T dao;

    public HangarAuthDao(T dao) {
        this.dao = dao;
    }

    public T get() {
        return dao;
    }
}